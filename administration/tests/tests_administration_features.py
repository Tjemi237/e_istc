from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from courses.models import Course, Module, Ressource, Category, CourseProgress
from evaluations.models import Activite, Soumission, Tentative
import json
import os
from django.core.management import call_command
from io import StringIO

class BackupRestoreTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='password', role=User.Role.ADMIN, is_staff=True, is_superuser=True)
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.student_user = User.objects.create_user(username='student', email='student@example.com', password='password', role=User.Role.ETUDIANT)

    def test_backup_and_restore_commands(self):
        # Create some data
        course = Course.objects.create(title='Cours de Sauvegarde avec accent é', description='Desc', teacher=self.teacher_user)
        
        # Backup
        out = StringIO()
        call_command('backup', stdout=out)
        self.assertIn('Successfully backed up the database to', out.getvalue())
        
        # Find the latest backup file
        backup_dir = 'backups'
        backup_files = os.listdir(backup_dir)
        latest_backup = max(backup_files, key=lambda f: os.path.getmtime(os.path.join(backup_dir, f)))
        backup_file_path = os.path.join(backup_dir, latest_backup)

        # Delete the data
        Course.objects.all().delete()
        User.objects.all().delete()
        self.assertEqual(Course.objects.count(), 0)
        self.assertEqual(User.objects.count(), 0)

        # Restore
        out = StringIO()
        call_command('restore', backup_file_path, stdout=out)
        self.assertIn('Successfully restored the database.', out.getvalue())

        # Verify data is restored
        course_count = Course.objects.count()
        user_count = User.objects.count()
        print(f"DEBUG: Course count after restore = {course_count}")
        print(f"DEBUG: User count after restore = {user_count}")
        self.assertEqual(course_count, 1)
        self.assertEqual(user_count, 3)
        self.assertTrue(Course.objects.filter(title='Cours de Sauvegarde avec accent é').exists())

class AdministrationAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='password', role=User.Role.ADMIN, is_staff=True, is_superuser=True)
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.student_user = User.objects.create_user(username='student', email='student@example.com', password='password', role=User.Role.ETUDIANT)

    # User Management API Tests
    def test_create_user_api_admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('administration:api_create_user'),
                                    {'username': 'newuser', 'email': 'new@example.com', 'first_name': 'New', 'last_name': 'User', 'role': User.Role.ETUDIANT, 'matricule': 'NEW001'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 4)

    def test_create_user_api_non_admin(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('administration:api_create_user'),
                                    json.dumps({'username': 'unauthuser', 'email': 'unauth@example.com', 'role': User.Role.ETUDIANT}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403) # Forbidden

    def test_user_detail_api_admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('administration:api_user_detail', args=[self.student_user.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['email'], 'student@example.com')

    def test_user_detail_api_non_admin(self):
        self.client.login(username='teacher', password='password')
        response = self.client.get(reverse('administration:api_user_detail', args=[self.student_user.id]))
        self.assertEqual(response.status_code, 403) # Forbidden

    def test_update_user_api_admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('administration:api_update_user', args=[self.student_user.id]),
                                    {'username': 'updatedstudent', 'email': 'updated@example.com', 'first_name': 'Updated', 'last_name': 'Student', 'role': User.Role.ETUDIANT, 'matricule': 'UPD001', 'specialite': '', 'is_active': True})
        self.assertEqual(response.status_code, 200)
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.email, 'updated@example.com')

    def test_update_user_api_non_admin(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('administration:api_update_user', args=[self.student_user.id]),
                                    json.dumps({'username': 'updatedstudent', 'email': 'updated@example.com', 'first_name': 'Updated', 'last_name': 'Student', 'role': User.Role.ETUDIANT, 'matricule': 'UPD001', 'specialite': '', 'is_active': True}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403) # Forbidden

    def test_delete_user_api_admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('administration:api_delete_user', args=[self.student_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 2) # 3 initial - 1 deleted

    def test_delete_user_api_non_admin(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('administration:api_delete_user', args=[self.student_user.id]))
        self.assertEqual(response.status_code, 403) # Forbidden

    # Course Management API Tests
    def test_create_course_api_admin(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('administration:api_create_course'),
                                    {'title': 'New Course', 'description': 'Desc', 'teacher': self.teacher_user.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Course.objects.count(), 1)

    def test_create_course_api_non_admin(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('administration:api_create_course'),
                                    json.dumps({'title': 'New Course', 'description': 'Desc', 'teacher': self.teacher_user.id}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403) # Forbidden

    def test_course_detail_api_admin(self):
        course = Course.objects.create(title='Detail Course', description='Desc', teacher=self.teacher_user)
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('administration:api_course_detail', args=[course.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['title'], 'Detail Course')

    def test_course_detail_api_non_admin(self):
        course = Course.objects.create(title='Detail Course', description='Desc', teacher=self.teacher_user)
        self.client.login(username='teacher', password='password')
        response = self.client.get(reverse('administration:api_course_detail', args=[course.id]))
        self.assertEqual(response.status_code, 403) # Forbidden

    def test_update_course_api_admin(self):
        course = Course.objects.create(title='Update Course', description='Desc', teacher=self.teacher_user)
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('administration:api_update_course', args=[course.id]),
                                    {'title': 'Updated Course', 'description': 'Updated Desc', 'teacher': self.teacher_user.id})
        self.assertEqual(response.status_code, 200)
        course.refresh_from_db()
        self.assertEqual(course.title, 'Updated Course')

    def test_update_course_api_non_admin(self):
        course = Course.objects.create(title='Update Course', description='Desc', teacher=self.teacher_user)
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('administration:api_update_course', args=[course.id]),
                                    json.dumps({'title': 'Updated Course', 'description': 'Updated Desc', 'teacher': self.teacher_user.id}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 403) # Forbidden

    def test_delete_course_api_admin(self):
        course = Course.objects.create(title='Delete Course', description='Desc', teacher=self.teacher_user)
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('administration:api_delete_course', args=[course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Course.objects.count(), 0)

    def test_delete_course_api_non_admin(self):
        course = Course.objects.create(title='Delete Course', description='Desc', teacher=self.teacher_user)
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('administration:api_delete_course', args=[course.id]))
        self.assertEqual(response.status_code, 403) # Forbidden

    def test_lock_user(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('administration:api_lock_user', args=[self.student_user.id]))
        self.assertEqual(response.status_code, 200)
        self.student_user.refresh_from_db()
        self.assertTrue(self.student_user.is_locked)

    def test_unlock_user(self):
        self.student_user.is_locked = True
        self.student_user.save()
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('administration:api_unlock_user', args=[self.student_user.id]))
        self.assertEqual(response.status_code, 200)
        self.student_user.refresh_from_db()
        self.assertFalse(self.student_user.is_locked)

class CourseProgressViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='password', role=User.Role.ADMIN, is_staff=True, is_superuser=True)
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.student_user = User.objects.create_user(username='student', email='student@example.com', password='password', role=User.Role.ETUDIANT)
        self.course = Course.objects.create(title='Progress Course', description='Desc', teacher=self.teacher_user)
        self.module = Module.objects.create(course=self.course, title='Module 1', order=1)
        self.ressource1 = Ressource.objects.create(module=self.module, title='Ressource 1')
        self.ressource2 = Ressource.objects.create(module=self.module, title='Ressource 2')
        self.course.students.add(self.student_user)

    def test_course_progress_view(self):
        progress, created = CourseProgress.objects.get_or_create(student=self.student_user, course=self.course)
        progress.completed_ressources.add(self.ressource1)
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('administration:course_progress', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '50.00%')

class CategoryManagementTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='password', role=User.Role.ADMIN, is_staff=True, is_superuser=True)
        self.category = Category.objects.create(name='Test Category', slug='test-category')

    def test_category_list_view(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('administration:category_management_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Category')

    def test_create_category_api(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('administration:api_create_category'),
                                    {'name': 'New Category', 'slug': 'new-category'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Category.objects.count(), 2)

    def test_update_category_api(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('administration:api_update_category', args=[self.category.id]),
                                    {'name': 'Updated Category', 'slug': 'updated-category'})
        self.assertEqual(response.status_code, 200)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category')

    def test_delete_category_api(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('administration:api_delete_category', args=[self.category.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Category.objects.count(), 0)

class ReportsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='password', role=User.Role.ADMIN, is_staff=True, is_superuser=True)
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.student1 = User.objects.create_user(username='student1', email='student1@example.com', password='password', role=User.Role.ETUDIANT)
        self.student2 = User.objects.create_user(username='student2', email='student2@example.com', password='password', role=User.Role.ETUDIANT)
        self.course = Course.objects.create(title='Reports Course', description='Desc', teacher=self.teacher_user)
        self.course.students.add(self.student1, self.student2)
        self.assignment = Activite.objects.create(course=self.course, title='Assignment 1', activity_type='DEVOIR')
        self.quiz = Activite.objects.create(course=self.course, title='Quiz 1', activity_type='QUIZ')
        Soumission.objects.create(activite=self.assignment, etudiant=self.student1, note=15)
        Soumission.objects.create(activite=self.assignment, etudiant=self.student2, note=18)
        Tentative.objects.create(activite=self.quiz, etudiant=self.student1, score=8)
        Tentative.objects.create(activite=self.quiz, etudiant=self.student2, score=9)

    def test_reports_page_view(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('administration:reports_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '16.50') # Average assignment grade
        self.assertContains(response, '8.50') # Average quiz score

class AuditLogsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='password', role=User.Role.ADMIN, is_staff=True, is_superuser=True)

    def test_audit_logs_page_view(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('administration:audit_logs_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Journaux d\'Audit')