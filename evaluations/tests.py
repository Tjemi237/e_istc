from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from courses.models import Course
from evaluations.models import Activite, Question, Choix, Soumission, Tentative, QuestionSondage, ReponseSondage
from evaluations.forms import ActiviteForm, QuestionForm, ChoixForm, SoumissionForm, QuestionSondageForm, ReponseSondageForm
import json
from datetime import datetime, timedelta
from django.core.files.uploadedfile import SimpleUploadedFile

class EvaluationModelTest(TestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.student_user = User.objects.create_user(username='student', email='student@example.com', password='password', role=User.Role.ETUDIANT)
        self.course = Course.objects.create(title='Test Course', description='Desc', teacher=self.teacher_user)

    def test_activite_creation(self):
        activite = Activite.objects.create(
            course=self.course,
            title='Devoir 1',
            activity_type=Activite.ActivityType.DEVOIR,
            due_date=datetime.now() + timedelta(days=7)
        )
        self.assertEqual(activite.title, 'Devoir 1')
        self.assertEqual(activite.course, self.course)

    def test_question_creation(self):
        activite = Activite.objects.create(
            course=self.course,
            title='Quiz 1',
            activity_type=Activite.ActivityType.QUIZ,
            due_date=datetime.now() + timedelta(days=7)
        )
        question = Question.objects.create(
            activite=activite,
            intitule='Quelle est la capitale de la France ?',
            type_question=Question.QuestionType.CHOIX_UNIQUE
        )
        self.assertEqual(question.intitule, 'Quelle est la capitale de la France ?')
        self.assertEqual(question.activite, activite)

    def test_choix_creation(self):
        activite = Activite.objects.create(
            course=self.course,
            title='Quiz 1',
            activity_type=Activite.ActivityType.QUIZ,
            due_date=datetime.now() + timedelta(days=7)
        )
        question = Question.objects.create(
            activite=activite,
            intitule='Quelle est la capitale de la France ?',
            type_question=Question.QuestionType.CHOIX_UNIQUE
        )
        choix = Choix.objects.create(
            question=question,
            texte='Paris',
            est_correct=True
        )
        self.assertEqual(choix.texte, 'Paris')
        self.assertEqual(choix.question, question)
        self.assertTrue(choix.est_correct)

    def test_soumission_creation(self):
        activite = Activite.objects.create(
            course=self.course,
            title='Devoir 1',
            activity_type=Activite.ActivityType.DEVOIR,
            due_date=datetime.now() + timedelta(days=7)
        )
        soumission = Soumission.objects.create(
            activite=activite,
            etudiant=self.student_user,
            fichier='path/to/file.pdf'
        )
        self.assertEqual(soumission.activite, activite)
        self.assertEqual(soumission.etudiant, self.student_user)

    def test_tentative_creation(self):
        activite = Activite.objects.create(
            course=self.course,
            title='Quiz 1',
            activity_type=Activite.ActivityType.QUIZ,
            due_date=datetime.now() + timedelta(days=7)
        )
        tentative = Tentative.objects.create(
            activite=activite,
            etudiant=self.student_user,
            score=10.5
        )
        self.assertEqual(tentative.activite, activite)
        self.assertEqual(tentative.etudiant, self.student_user)
        self.assertEqual(tentative.score, 10.5)

    def test_question_sondage_creation(self):
        activite = Activite.objects.create(
            course=self.course,
            title='Sondage 1',
            activity_type=Activite.ActivityType.SONDAGE,
        )
        question = QuestionSondage.objects.create(
            activite=activite,
            intitule='Votre avis sur le cours ?',
        )
        self.assertEqual(question.intitule, 'Votre avis sur le cours ?')
        self.assertEqual(question.activite, activite)

    def test_reponse_sondage_creation(self):
        activite = Activite.objects.create(
            course=self.course,
            title='Sondage 1',
            activity_type=Activite.ActivityType.SONDAGE,
        )
        question = QuestionSondage.objects.create(
            activite=activite,
            intitule='Votre avis sur le cours ?',
        )
        reponse = ReponseSondage.objects.create(
            question=question,
            etudiant=self.student_user,
            reponse='Très intéressant !',
        )
        self.assertEqual(reponse.reponse, 'Très intéressant !')
        self.assertEqual(reponse.question, question)
        self.assertEqual(reponse.etudiant, self.student_user)


class EvaluationFormTest(TestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.course = Course.objects.create(title='Test Course', description='Desc', teacher=self.teacher_user)

    def test_activite_form_valid(self):
        form_data = {
            'title': 'New Activity',
            'description': 'Desc',
            'activity_type': Activite.ActivityType.DEVOIR,
            'due_date': datetime.now().strftime('%Y-%m-%dT%H:%M')
        }
        form = ActiviteForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_activite_form_invalid(self):
        form_data = {
            'title': '',
            'activity_type': Activite.ActivityType.DEVOIR,
        }
        form = ActiviteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_question_form_valid(self):
        form_data = {
            'intitule': 'New Question',
            'type_question': Question.QuestionType.CHOIX_UNIQUE
        }
        form = QuestionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_question_form_invalid(self):
        form_data = {
            'intitule': '',
        }
        form = QuestionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('intitule', form.errors)

    def test_choix_form_valid(self):
        form_data = {
            'texte': 'Option 1',
            'est_correct': True
        }
        form = ChoixForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_soumission_form_valid(self):
        # Create a dummy file
        dummy_file = SimpleUploadedFile("file.pdf", b"file_content", content_type="application/pdf")
        form_data = {}
        file_data = {'fichier': dummy_file}
        form = SoumissionForm(data=form_data, files=file_data)
        self.assertTrue(form.is_valid())

    def test_question_sondage_form_valid(self):
        form_data = {
            'intitule': 'Nouvelle question de sondage',
        }
        form = QuestionSondageForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_reponse_sondage_form_valid(self):
        form_data = {
            'reponse': 'Ma réponse au sondage',
        }
        form = ReponseSondageForm(data=form_data)
        self.assertTrue(form.is_valid())


class EvaluationAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='password', role=User.Role.ADMIN)
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.student_user = User.objects.create_user(username='student', email='student@example.com', password='password', role=User.Role.ETUDIANT)
        self.course = Course.objects.create(title='API Course', description='Desc', teacher=self.teacher_user)
        self.quiz_activity = Activite.objects.create(course=self.course, title='API Quiz', activity_type=Activite.ActivityType.QUIZ)
        self.devoir_activity = Activite.objects.create(course=self.course, title='API Devoir', activity_type=Activite.ActivityType.DEVOIR)
        self.sondage_activity = Activite.objects.create(course=self.course, title='API Sondage', activity_type=Activite.ActivityType.SONDAGE)
        self.question = Question.objects.create(activite=self.quiz_activity, intitule='Q1', type_question=Question.QuestionType.CHOIX_UNIQUE)
        self.choix1 = Choix.objects.create(question=self.question, texte='C1', est_correct=True)
        self.choix2 = Choix.objects.create(question=self.question, texte='C2', est_correct=False)
        self.submission = Soumission.objects.create(activite=self.devoir_activity, etudiant=self.student_user, fichier='dummy.pdf')
        self.course.students.add(self.student_user)

    def test_create_activity_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('evaluations:api_create_activity', args=[self.course.id]),
                                    json.dumps({'title': 'New API Activity', 'activity_type': 'DEVOIR', 'due_date': '2025-12-31T23:59'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Activite.objects.count(), 3)

    def test_update_activity_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('evaluations:api_update_activity', args=[self.quiz_activity.id]),
                                    json.dumps({'title': 'Updated Quiz', 'activity_type': 'QUIZ', 'due_date': '2025-12-31T23:59'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.quiz_activity.refresh_from_db()
        self.assertEqual(self.quiz_activity.title, 'Updated Quiz')

    def test_delete_activity_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('evaluations:api_delete_activity', args=[self.quiz_activity.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Activite.objects.count(), 1)

    def test_create_question_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('evaluations:api_create_question', args=[self.quiz_activity.id]),
                                    json.dumps({'intitule': 'New Q', 'type_question': 'UNIQUE', 'choices': [{'text': 'Opt1', 'is_correct': True}]}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 2)

    def test_update_question_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('evaluations:api_update_question', args=[self.question.id]),
                                    json.dumps({'intitule': 'Updated Q', 'type_question': 'MULTIPLE', 'choices': [{'text': 'OptA', 'is_correct': True}, {'text': 'OptB', 'is_correct': False}]}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.question.refresh_from_db()
        self.assertEqual(self.question.intitule, 'Updated Q')
        self.assertEqual(self.question.choix.count(), 2)

    def test_delete_question_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('evaluations:api_delete_question', args=[self.question.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Question.objects.count(), 0)

    def test_grade_submission_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('evaluations:api_grade_submission', args=[self.submission.id]),
                                    json.dumps({'note': 15.5}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.submission.refresh_from_db()
        self.assertEqual(self.submission.note, 15.5)

    def test_list_submissions_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.get(reverse('evaluations:api_list_submissions', args=[self.devoir_activity.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['soumissions']), 1)
        self.assertEqual(data['soumissions'][0]['id'], self.submission.id)

    def test_create_sondage_question_api(self):
        self.client.login(username='teacher', password='password')
        sondage_activity = Activite.objects.create(course=self.course, title='API Sondage', activity_type=Activite.ActivityType.SONDAGE)
        response = self.client.post(reverse('evaluations:api_create_sondage_question', args=[sondage_activity.id]),
                                    json.dumps({'intitule': 'Question Sondage 1'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(QuestionSondage.objects.count(), 1)

    def test_submit_sondage_response_api(self):
        sondage_activity = Activite.objects.create(course=self.course, title='API Sondage', activity_type=Activite.ActivityType.SONDAGE)
        question_sondage = QuestionSondage.objects.create(activite=sondage_activity, intitule='Question Sondage 1')
        self.client.login(username='student', password='password')
        response = self.client.post(reverse('evaluations:api_submit_sondage_response', args=[question_sondage.id]),
                                    json.dumps({'reponse': 'Ma réponse au sondage'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ReponseSondage.objects.count(), 1)

    def test_list_sondage_questions_api(self):
        sondage_activity = Activite.objects.create(course=self.course, title='API Sondage', activity_type=Activite.ActivityType.SONDAGE)
        QuestionSondage.objects.create(activite=sondage_activity, intitule='Question Sondage 1')
        self.client.login(username='teacher', password='password')
        response = self.client.get(reverse('evaluations:api_list_sondage_questions', args=[sondage_activity.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['questions']), 1)

    def test_delete_sondage_question_api(self):
        sondage_activity = Activite.objects.create(course=self.course, title='API Sondage', activity_type=Activite.ActivityType.SONDAGE)
        question_sondage = QuestionSondage.objects.create(activite=sondage_activity, intitule='Question Sondage 1')
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('evaluations:api_delete_sondage_question', args=[question_sondage.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(QuestionSondage.objects.count(), 0)
