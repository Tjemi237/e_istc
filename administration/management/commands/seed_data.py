from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from faker import Faker
import random
import os
from django.core import serializers

from users.models import User
from courses.models import Course, Category, Module, Ressource, Annonce
from evaluations.models import Activite, Question, Choix, Soumission, Tentative, QuestionSondage, ReponseSondage
from forums.models import SujetDiscussion, MessageForum
from messaging.models import Conversation, Message as ChatMessage
from platform_settings.models import PlatformSettings

class Command(BaseCommand):
    help = 'Seeds the database with realistic data.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Deleting all existing data...'))
        # Clear existing data
        User.objects.all().delete()
        Category.objects.all().delete()
        Course.objects.all().delete()
        Activite.objects.all().delete()
        SujetDiscussion.objects.all().delete()
        Conversation.objects.all().delete()
        PlatformSettings.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All existing data deleted.'))

        fake = Faker('fr_FR')

        self.stdout.write(self.style.MIGRATE_HEADING('Creating Users...'))
        # Create Admin
        admin_user = User.objects.create(
            username='admin',
            email='admin@istc.ci',
            first_name='Admin',
            last_name='ISTC',
            password=make_password('adminpassword'),
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        self.stdout.write(self.style.SUCCESS(f'Created Admin: {admin_user.email}'))

        # Create Teachers
        teachers = []
        for _ in range(5):
            teacher = User.objects.create(
                username=fake.user_name(),
                email=fake.unique.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password=make_password('teacherpassword'),
                role=User.Role.ENSEIGNANT,
                specialite=fake.job(),
                is_active=True,
            )
            teachers.append(teacher)
            self.stdout.write(self.style.SUCCESS(f'Created Teacher: {teacher.email}'))

        # Create Students
        students = []
        for i in range(20):
            matricule = f'ISTC{random.randint(1000, 9999)}'
            student = User.objects.create(
                username=matricule,
                email=fake.unique.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password=make_password('studentpassword'),
                role=User.Role.ETUDIANT,
                matricule=matricule,
                is_active=True,
            )
            students.append(student)
            self.stdout.write(self.style.SUCCESS(f'Created Student: {student.email}'))

        self.stdout.write(self.style.MIGRATE_HEADING('Creating Categories...'))
        categories_data = [
            {'name': 'Informatique', 'slug': 'informatique'},
            {'name': 'Gestion', 'slug': 'gestion'},
            {'name': 'Santé', 'slug': 'sante'},
            {'name': 'Électronique', 'slug': 'electronique'},
            {'name': 'Design', 'slug': 'design'},
        ]
        categories = []
        for cat_data in categories_data:
            category = Category.objects.create(**cat_data)
            categories.append(category)
            self.stdout.write(self.style.SUCCESS(f'Created Category: {category.name}'))

        self.stdout.write(self.style.MIGRATE_HEADING('Creating Courses...'))
        courses = []
        for _ in range(10):
            course = Course.objects.create(
                title=fake.catch_phrase(),
                description=fake.paragraph(nb_sentences=5),
                teacher=random.choice(teachers),
                category=random.choice(categories),
                visio_link=fake.url() if random.random() > 0.5 else None,
                visio_date=fake.date_time_between(start_date='now', end_date='+30d') if random.random() > 0.5 else None,
            )
            courses.append(course)
            self.stdout.write(self.style.SUCCESS(f'Created Course: {course.title}'))

            # Enroll some students in the course
            num_students_to_enroll = random.randint(5, 15)
            enrolled_students = random.sample(students, num_students_to_enroll)
            for student in enrolled_students:
                course.students.add(student)
            self.stdout.write(self.style.SUCCESS(f'Enrolled {num_students_to_enroll} students in {course.title}'))

            self.stdout.write(self.style.MIGRATE_HEADING(f'Creating Modules and Resources for {course.title}...'))
            for i in range(random.randint(2, 5)):
                module = Module.objects.create(
                    course=course,
                    title=f'Module {i+1}: {fake.bs()}',
                    description=fake.paragraph(nb_sentences=2),
                    order=i+1,
                )
                for _ in range(random.randint(1, 4)):
                    Ressource.objects.create(
                        module=module,
                        title=fake.sentence(nb_words=4),
                        url=fake.url() if random.random() > 0.5 else None,
                        # file=... # Skipping file upload for seeding simplicity
                    )
                self.stdout.write(self.style.SUCCESS(f'  Created Module: {module.title}'))

            self.stdout.write(self.style.MIGRATE_HEADING(f'Creating Announcements for {course.title}...'))
            for _ in range(random.randint(1, 3)):
                Annonce.objects.create(
                    cours=course,
                    titre=fake.sentence(nb_words=6),
                    contenu=fake.paragraph(nb_sentences=3),
                )
            self.stdout.write(self.style.SUCCESS(f'  Created Announcements for {course.title}'))

            self.stdout.write(self.style.MIGRATE_HEADING(f'Creating Activities for {course.title}...'))
            # Create Assignments
            for _ in range(random.randint(1, 3)):
                assignment = Activite.objects.create(
                    course=course,
                    title=f'Devoir: {fake.catch_phrase()}',
                    description=fake.paragraph(nb_sentences=2),
                    activity_type=Activite.ActivityType.DEVOIR,
                    due_date=fake.date_time_between(start_date='now', end_date='+15d'),
                )
                # Create some submissions
                for student in random.sample(enrolled_students, random.randint(0, len(enrolled_students))):
                    if random.random() > 0.3: # Simulate some students not submitting
                        Soumission.objects.create(
                            activite=assignment,
                            etudiant=student,
                            # fichier=... # Skipping file upload
                            date_soumission=fake.date_time_between(start_date='-7d', end_date='now'),
                            note=random.uniform(0, 20) if random.random() > 0.2 else None, # Some might not be graded yet
                            commentaires_enseignant=fake.sentence() if random.random() > 0.5 else None,
                        )

            # Create Quizzes
            for _ in range(random.randint(1, 2)):
                quiz = Activite.objects.create(
                    course=course,
                    title=f'Quiz: {fake.catch_phrase()}',
                    description=fake.paragraph(nb_sentences=2),
                    activity_type=Activite.ActivityType.QUIZ,
                    due_date=fake.date_time_between(start_date='now', end_date='+10d'),
                )
                # Add questions and choices
                for q_num in range(random.randint(3, 7)):
                    question = Question.objects.create(
                        activite=quiz,
                        intitule=fake.sentence(nb_words=8, variable_nb_words=False) + '?',
                        type_question=random.choice([Question.QuestionType.CHOIX_UNIQUE, Question.QuestionType.CHOIX_MULTIPLE]),
                    )
                    correct_choice_text = fake.word()
                    Choix.objects.create(question=question, texte=correct_choice_text, est_correct=True)
                    for _ in range(random.randint(2, 4)):
                        Choix.objects.create(question=question, texte=fake.word(), est_correct=False)
                
                # Create some quiz attempts
                for student in random.sample(enrolled_students, random.randint(0, len(enrolled_students))):
                    if random.random() > 0.3: # Simulate some students not attempting
                        Tentative.objects.create(
                            activite=quiz,
                            etudiant=student,
                            score=random.uniform(0, quiz.questions.count()),
                            date_tentative=fake.date_time_between(start_date='-5d', end_date='now'),
                        )

            # Create Surveys
            for _ in range(random.randint(1, 2)):
                survey = Activite.objects.create(
                    course=course,
                    title=f'Sondage: {fake.catch_phrase()}',
                    description=fake.paragraph(nb_sentences=2),
                    activity_type=Activite.ActivityType.SONDAGE,
                    due_date=fake.date_time_between(start_date='now', end_date='+7d'),
                )
                # Add survey questions
                for q_num in range(random.randint(3, 5)):
                    QuestionSondage.objects.create(
                        activite=survey,
                        intitule=fake.sentence(nb_words=10, variable_nb_words=False) + '?',
                    )
                # Create some survey responses
                for student in random.sample(enrolled_students, random.randint(0, len(enrolled_students))):
                    if random.random() > 0.3: # Simulate some students not responding
                        for q_sondage in survey.questions_sondage.all():
                            ReponseSondage.objects.create(
                                question=q_sondage,
                                etudiant=student,
                                reponse=fake.paragraph(nb_sentences=1),
                            )

        self.stdout.write(self.style.MIGRATE_HEADING('Creating Forum Discussions and Messages...'))
        for course in courses:
            for _ in range(random.randint(1, 5)):
                author = random.choice(list(course.students.all()) + [course.teacher])
                sujet = SujetDiscussion.objects.create(
                    cours=course,
                    titre=fake.sentence(nb_words=7),
                    auteur=author,
                )
                for _ in range(random.randint(2, 10)):
                    msg_author = random.choice(list(course.students.all()) + [course.teacher])
                    MessageForum.objects.create(
                        sujet=sujet,
                        auteur=msg_author,
                        contenu=fake.paragraph(nb_sentences=2),
                    )

        self.stdout.write(self.style.MIGRATE_HEADING('Creating Messaging Conversations...'))
        for _ in range(10):
            participants = random.sample(list(User.objects.all()), random.randint(2, 3))
            conversation = Conversation.objects.create()
            conversation.participants.set(participants)
            for _ in range(random.randint(3, 10)):
                sender = random.choice(participants)
                ChatMessage.objects.create(
                    conversation=conversation,
                    sender=sender,
                    content=fake.sentence(nb_words=10),
                    is_read=fake.boolean(chance_of_getting_true=70),
                )

        self.stdout.write(self.style.MIGRATE_HEADING('Creating Platform Settings...'))
        PlatformSettings.objects.create(
            primary_color='#0D47A1',
            secondary_color='#FF9800',
            # logo=... # Skipping logo for seeding simplicity
        )
        self.stdout.write(self.style.SUCCESS('Platform Settings created.'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
