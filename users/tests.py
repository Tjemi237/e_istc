import json
from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from users.forms import CustomUserCreationForm, CustomUserChangeForm
from courses.models import Course
from evaluations.models import Activite, QuestionSondage, ReponseSondage

class UserModelTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('password'))
        self.assertEqual(user.role, User.Role.ETUDIANT) # Default role

    def test_admin_user_creation(self):
        admin_user = User.objects.create_user(username='adminuser', email='admin@example.com', password='password', role=User.Role.ADMIN, is_staff=True, is_superuser=True)
        self.assertEqual(admin_user.role, User.Role.ADMIN)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_teacher_user_creation(self):
        teacher_user = User.objects.create_user(username='teacheruser', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.assertEqual(teacher_user.role, User.Role.ENSEIGNANT)

    def test_user_roles(self):
        student = User.objects.create_user(username='student1', email='student1@example.com', password='pass', role=User.Role.ETUDIANT)
        teacher = User.objects.create_user(username='teacher1', email='teacher1@example.com', password='pass', role=User.Role.ENSEIGNANT)
        admin = User.objects.create_user(username='admin1', email='admin1@example.com', password='pass', role=User.Role.ADMIN, is_staff=True, is_superuser=True)

        self.assertTrue(student.is_etudiant)
        self.assertFalse(student.is_enseignant)
        self.assertFalse(student.is_admin)

        self.assertFalse(teacher.is_etudiant)
        self.assertTrue(teacher.is_enseignant)
        self.assertFalse(teacher.is_admin)

        self.assertFalse(admin.is_etudiant)
        self.assertFalse(admin.is_enseignant)
        self.assertTrue(admin.is_admin)


class UserFormTest(TestCase):
    def test_custom_user_creation_form_valid(self):
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': User.Role.ETUDIANT,
            'matricule': 'MAT123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_custom_user_creation_form_invalid(self):
        form_data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'role': User.Role.ETUDIANT,
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_custom_user_change_form_valid(self):
        user = User.objects.create_user(username='changeuser', email='change@example.com', password='password')
        form_data = {
            'username': 'changeduser',
            'email': 'changed@example.com',
            'first_name': 'Changed',
            'last_name': 'User',
            'role': User.Role.ENSEIGNANT,
            'is_active': True
        }
        form = CustomUserChangeForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid(), form.errors)


class UserViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='password', role=User.Role.ADMIN)
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.student_user = User.objects.create_user(username='student', email='student@example.com', password='password', role=User.Role.ETUDIANT)

    def test_login_view(self):
        # Create a user for login test
        User.objects.create_user(username='testuser_login', email='login@example.com', password='password')
        response = self.client.post(reverse('users:login'), {'username': 'testuser_login', 'password': 'password'})
        self.assertEqual(response.status_code, 302) # Redirects on successful login

    def test_logout_view(self):
        # Create a user for logout test
        User.objects.create_user(username='testuser_logout', email='logout@example.com', password='password')
        self.client.login(username='testuser_logout', password='password')
        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, 302) # Redirects on successful logout

    def test_etudiant_dashboard_view(self):
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('users:etudiant_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tableau de Bord Étudiant')

    def test_enseignant_dashboard_view(self):
        self.client.login(username='teacher', password='password')
        response = self.client.get(reverse('users:enseignant_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tableau de Bord Enseignant')

    def test_admin_access_to_user_management(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('administration:user_management'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gestion des Utilisateurs')

    def test_course_search(self):
        Course.objects.create(title='Python Basics', description='Learn Python', teacher=self.teacher_user)
        Course.objects.create(title='Java Advanced', description='Learn Java', teacher=self.teacher_user)
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('users:etudiant_dashboard') + '?q=Python')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Basics')
        self.assertNotContains(response, 'Java Advanced')


class UserAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='password', role=User.Role.ADMIN)
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.student_user = User.objects.create_user(username='student', email='student@example.com', password='password', role=User.Role.ETUDIANT)

    def test_create_user_api(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('administration:api_create_user'),
                                    {'username': 'newapiuser', 'email': 'newapi@example.com', 'first_name': 'API', 'last_name': 'User', 'role': User.Role.ETUDIANT, 'matricule': 'API001'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 4) # 3 initial users + 1 new

    def test_user_detail_api(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('administration:api_user_detail', args=[self.student_user.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['email'], 'student@example.com')

    def test_update_user_api(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('administration:api_update_user', args=[self.student_user.id]),
                                    {'username': 'updatedstudent', 'email': 'updated@example.com', 'first_name': 'Updated', 'last_name': 'Student', 'role': User.Role.ETUDIANT, 'matricule': 'UPD001'})
        self.assertEqual(response.status_code, 200)
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.username, 'updatedstudent')

    def test_delete_user_api(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('administration:api_delete_user', args=[self.student_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 2) # 3 initial users - 1 deleted

class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.student_user = User.objects.create_user(username='student', email='student@example.com', password='password', role=User.Role.ETUDIANT, first_name='John', last_name='Doe', matricule='ETU12345')

    def test_profile_view_get(self):
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mon Profil')
        self.assertContains(response, 'John')

    def test_profile_view_post_update(self):
        self.client.login(username='student', password='password')
        response = self.client.post(reverse('users:profile'), {
            'first_name': 'John-Updated',
            'last_name': 'Doe',
            'email': 'student@example.com',
            'matricule': self.student_user.matricule,
            'specialite': ''
        })
        self.assertEqual(response.status_code, 302) # Redirect on success
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.first_name, 'John-Updated')

class SondageViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.student_user = User.objects.create_user(username='student', email='student@example.com', password='password', role=User.Role.ETUDIANT)
        self.course = Course.objects.create(title='Sondage Course', description='Desc', teacher=self.teacher_user)
        self.course.students.add(self.student_user)
        self.sondage_activity = Activite.objects.create(course=self.course, title='Test Sondage', activity_type=Activite.ActivityType.SONDAGE)
        self.question1 = QuestionSondage.objects.create(activite=self.sondage_activity, intitule='Question 1')
        self.question2 = QuestionSondage.objects.create(activite=self.sondage_activity, intitule='Question 2')

    def test_take_sondage_view_get(self):
        self.client.login(username='student', password='password')
        response = self.client.get(reverse('users:take_sondage', args=[self.sondage_activity.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Question 1')
        self.assertContains(response, 'Question 2')

    def test_take_sondage_view_post(self):
        self.client.login(username='student', password='password')
        response = self.client.post(reverse('users:take_sondage', args=[self.sondage_activity.id]), {
            f'question_{self.question1.id}': 'Réponse à la question 1',
            f'question_{self.question2.id}': 'Réponse à la question 2',
        })
        self.assertEqual(response.status_code, 302) # Redirects to course detail
        self.assertEqual(ReponseSondage.objects.count(), 2)
        self.assertTrue(ReponseSondage.objects.filter(question=self.question1, etudiant=self.student_user, reponse='Réponse à la question 1').exists())

    def test_take_sondage_already_responded(self):
        ReponseSondage.objects.create(question=self.question1, etudiant=self.student_user, reponse='Old response')
        self.client.login(username='student', password='password')
        response = self.client.post(reverse('users:take_sondage', args=[self.sondage_activity.id]), {
            f'question_{self.question1.id}': 'New response',
        })
        self.assertEqual(response.status_code, 302) # Should still redirect, but not create new response
        self.assertEqual(ReponseSondage.objects.count(), 1) # Should not create a duplicate
