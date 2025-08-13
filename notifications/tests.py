from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from courses.models import Course, Annonce
from messaging.models import Conversation, Message
from .models import Notification

class NotificationSignalTest(TestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.student_user = User.objects.create_user(username='student', email='student@example.com', password='password', role=User.Role.ETUDIANT)
        self.course = Course.objects.create(title='Notification Course', description='Desc', teacher=self.teacher_user)
        self.course.students.add(self.student_user)

    def test_annonce_notification(self):
        Annonce.objects.create(cours=self.course, titre='Test Annonce', contenu='Contenu')
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.student_user)
        self.assertIn('Nouvelle annonce', notification.message)

    def test_message_notification(self):
        conversation = Conversation.objects.create()
        conversation.participants.add(self.teacher_user, self.student_user)
        Message.objects.create(conversation=conversation, sender=self.teacher_user, content='Hello')
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.student_user)
        self.assertIn('Nouveau message', notification.message)

class NotificationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student_user = User.objects.create_user(username='student', email='student@example.com', password='password', role=User.Role.ETUDIANT)
        self.notification = Notification.objects.create(user=self.student_user, message='Test notification')

    def test_notification_list_view(self):
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('notifications:notification_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test notification')

    def test_mark_as_read_api(self):
        self.client.login(username='student', password='password')
        response = self.client.post(reverse('notifications:mark_as_read', args=[self.notification.id]))
        self.assertEqual(response.status_code, 200)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)