from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from courses.models import Course
from forums.models import SujetDiscussion, MessageForum

class ForumModelTest(TestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.student_user = User.objects.create_user(username='student', email='student@example.com', password='password', role=User.Role.ETUDIANT)
        self.course = Course.objects.create(title='Test Course', description='Desc', teacher=self.teacher_user)

    def test_sujet_creation(self):
        sujet = SujetDiscussion.objects.create(
            cours=self.course,
            titre='Test Sujet',
            auteur=self.teacher_user
        )
        self.assertEqual(sujet.titre, 'Test Sujet')
        self.assertEqual(sujet.cours, self.course)
        self.assertEqual(sujet.auteur, self.teacher_user)

    def test_message_creation(self):
        sujet = SujetDiscussion.objects.create(
            cours=self.course,
            titre='Test Sujet',
            auteur=self.teacher_user
        )
        message = MessageForum.objects.create(
            sujet=sujet,
            auteur=self.student_user,
            contenu='Test Message'
        )
        self.assertEqual(message.contenu, 'Test Message')
        self.assertEqual(message.sujet, sujet)
        self.assertEqual(message.auteur, self.student_user)


class ForumViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='password', role=User.Role.ADMIN, is_staff=True, is_superuser=True)
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.student_user = User.objects.create_user(username='student', email='student@example.com', password='password', role=User.Role.ETUDIANT)
        self.other_student = User.objects.create_user(username='other_student', email='other@example.com', password='password', role=User.Role.ETUDIANT)

        self.course = Course.objects.create(title='Forum Course', description='Desc', teacher=self.teacher_user)
        self.course.students.add(self.student_user)

        self.sujet = SujetDiscussion.objects.create(cours=self.course, titre='Test Sujet', auteur=self.teacher_user)
        self.message = MessageForum.objects.create(sujet=self.sujet, auteur=self.student_user, contenu='Test Message')

    def test_forum_cours_view(self):
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('forums:forum_cours', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Sujet')

    def test_details_sujet_view(self):
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('forums:details_sujet', args=[self.sujet.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Message')

    def test_creer_sujet_view(self):
        self.client.login(username='student', password='password')
        response = self.client.post(reverse('forums:creer_sujet', args=[self.course.id]), {
            'titre': 'Nouveau Sujet',
            'contenu': 'Contenu du nouveau sujet'
        })
        self.assertEqual(response.status_code, 302) # Redirect
        self.assertEqual(SujetDiscussion.objects.count(), 2)
        self.assertEqual(MessageForum.objects.count(), 2) # Original message + new message

    def test_ajouter_message_view(self):
        self.client.login(username='student', password='password')
        response = self.client.post(reverse('forums:ajouter_message', args=[self.sujet.id]), {
            'contenu': 'Nouvelle réponse'
        })
        self.assertEqual(response.status_code, 302) # Redirect
        self.assertEqual(MessageForum.objects.count(), 2) # Original message + new message

    def test_supprimer_message_view(self):
        self.client.login(username='student', password='password')
        response = self.client.post(reverse('forums:supprimer_message', args=[self.message.id]))
        self.assertEqual(response.status_code, 302) # Redirect
        self.assertEqual(MessageForum.objects.count(), 0)
        self.assertEqual(SujetDiscussion.objects.count(), 0) # Sujet should be deleted if no messages left

    def test_supprimer_sujet_view(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('forums:supprimer_sujet', args=[self.sujet.id]))
        self.assertEqual(response.status_code, 302) # Redirect
        self.assertEqual(SujetDiscussion.objects.count(), 0)
        self.assertEqual(MessageForum.objects.count(), 0)

    # Permission tests
    def test_forum_cours_permission(self):
        self.client.login(username='other_student', password='password') # Not enrolled
        response = self.client.get(reverse('forums:forum_cours', args=[self.course.id]))
        self.assertEqual(response.status_code, 403) # Permission Denied

    def test_creer_sujet_permission(self):
        self.client.login(username='other_student', password='password')
        response = self.client.post(reverse('forums:creer_sujet', args=[self.course.id]), {
            'titre': 'Unauthorized Sujet',
            'contenu': 'Content'
        })
        self.assertEqual(response.status_code, 403)

    def test_supprimer_message_permission(self):
        self.client.login(username='other_student', password='password')
        response = self.client.post(reverse('forums:supprimer_message', args=[self.message.id]))
        self.assertEqual(response.status_code, 403)

    def test_supprimer_sujet_permission(self):
        self.client.login(username='other_student', password='password')
        response = self.client.post(reverse('forums:supprimer_sujet', args=[self.sujet.id]))
        self.assertEqual(response.status_code, 403)