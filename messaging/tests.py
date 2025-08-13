import json
from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from messaging.models import Conversation, Message

class MessagingModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='password')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='password')
        self.user3 = User.objects.create_user(username='user3', email='user3@example.com', password='password')

    def test_conversation_creation(self):
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)
        self.assertEqual(conversation.participants.count(), 2)
        self.assertIn(self.user1, conversation.participants.all())
        self.assertIn(self.user2, conversation.participants.all())

    def test_message_creation(self):
        conversation = Conversation.objects.create()
        conversation.participants.add(self.user1, self.user2)
        message = Message.objects.create(conversation=conversation, sender=self.user1, content='Hello')
        self.assertEqual(message.content, 'Hello')
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.conversation, conversation)
        self.assertFalse(message.is_read)


class MessagingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='password')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='password')
        self.user3 = User.objects.create_user(username='user3', email='user3@example.com', password='password')

        self.conversation1 = Conversation.objects.create()
        self.conversation1.participants.add(self.user1, self.user2)
        Message.objects.create(conversation=self.conversation1, sender=self.user1, content='Hi user2')
        Message.objects.create(conversation=self.conversation1, sender=self.user2, content='Hi user1')
        self.unread_message = Message.objects.create(conversation=self.conversation1, sender=self.user2, content='Unread message', is_read=False)

        self.conversation2 = Conversation.objects.create()
        self.conversation2.participants.add(self.user1, self.user3)
        Message.objects.create(conversation=self.conversation2, sender=self.user1, content='Hi user3')

    def test_inbox_view(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('messaging:inbox'))
        self.assertEqual(response.status_code, 200)
        # Check for the last message content of conv1 (which is 'Unread message')
        self.assertContains(response, 'Unread message')
        # Check for the last message content of conv2 (which is 'Hi user3')
        self.assertContains(response, 'Hi user3')
        # Check for the unread messages badge in the navigation bar
        self.assertContains(response, 'Messagerie <span class="badge bg-danger">2</span>')

    def test_conversation_detail_view(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('messaging:conversation_detail', args=[self.conversation1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Hi user2')
        self.assertContains(response, 'Unread message')
        # Check if unread message is marked as read after viewing
        self.unread_message.refresh_from_db()
        self.assertTrue(self.unread_message.is_read)

    def test_new_conversation_view_existing(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('messaging:new_conversation', args=[self.user2.id]))
        self.assertRedirects(response, reverse('messaging:conversation_detail', args=[self.conversation1.id]))

    def test_new_conversation_view_new(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('messaging:new_conversation', args=[self.user3.id]))
        # Should redirect to the new conversation detail page
        new_conversation = Conversation.objects.filter(participants=self.user1).filter(participants=self.user3).first()
        self.assertRedirects(response, reverse('messaging:conversation_detail', args=[new_conversation.id]))

    def test_search_users_api(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('messaging:search_users') + '?q=user2')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['users']), 1)
        self.assertEqual(data['users'][0]['name'], f'{self.user2.first_name} {self.user2.last_name}') # Changed from 'username' to 'name'

    def test_send_message_in_conversation_detail(self):
        self.client.login(username='user1', password='password')
        message_count_before = Message.objects.count()
        response = self.client.post(reverse('messaging:conversation_detail', args=[self.conversation1.id]), {'content': 'New message from user1'})
        self.assertRedirects(response, reverse('messaging:conversation_detail', args=[self.conversation1.id]))
        self.assertEqual(Message.objects.count(), message_count_before + 1)
        self.assertEqual(Message.objects.last().content, 'New message from user1')

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.get(reverse('messaging:inbox'))
        self.assertRedirects(response, reverse('users:login') + '?next=/messaging/')
