from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from courses.models import Course, Module, Ressource, Annonce, CourseProgress
from courses.forms import CourseForm, ModuleForm, RessourceForm, AnnonceForm
import json

class CourseModelTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='password', role=User.Role.ADMIN)
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.student_user = User.objects.create_user(username='student', email='student@example.com', password='password', role=User.Role.ETUDIANT)

    def test_course_creation(self):
        course = Course.objects.create(
            title='Test Course',
            description='This is a test course.',
            teacher=self.teacher_user
        )
        self.assertEqual(course.title, 'Test Course')
        self.assertEqual(course.teacher, self.teacher_user)

    def test_module_creation(self):
        course = Course.objects.create(
            title='Test Course',
            description='This is a test course.',
            teacher=self.teacher_user
        )
        module = Module.objects.create(
            course=course,
            title='Test Module',
            description='This is a test module.',
            order=1
        )
        self.assertEqual(module.title, 'Test Module')
        self.assertEqual(module.course, course)
        self.assertEqual(module.order, 1)

    def test_ressource_creation(self):
        course = Course.objects.create(
            title='Test Course',
            description='This is a test course.',
            teacher=self.teacher_user
        )
        module = Module.objects.create(
            course=course,
            title='Test Module',
            description='This is a test module.',
            order=1
        )
        ressource = Ressource.objects.create(
            module=module,
            title='Test Ressource',
            url='http://example.com/resource'
        )
        self.assertEqual(ressource.title, 'Test Ressource')
        self.assertEqual(ressource.module, module)
        self.assertEqual(ressource.url, 'http://example.com/resource')

    def test_annonce_creation(self):
        course = Course.objects.create(
            title='Test Course',
            description='This is a test course.',
            teacher=self.teacher_user
        )
        annonce = Annonce.objects.create(
            cours=course,
            titre='Test Annonce',
            contenu='This is a test announcement.'
        )
        self.assertEqual(annonce.titre, 'Test Annonce')
        self.assertEqual(annonce.cours, course)

    def test_course_students_relation(self):
        course = Course.objects.create(
            title='Test Course',
            description='This is a test course.',
            teacher=self.teacher_user
        )
        course.students.add(self.student_user)
        self.assertIn(self.student_user, course.students.all())

    def test_course_modules_relation(self):
        course = Course.objects.create(
            title='Test Course',
            description='This is a test course.',
            teacher=self.teacher_user
        )
        module = Module.objects.create(
            course=course,
            title='Test Module',
            description='This is a test module.',
            order=1
        )
        self.assertIn(module, course.modules.all())

    def test_module_ressources_relation(self):
        course = Course.objects.create(
            title='Test Course',
            description='This is a test course.',
            teacher=self.teacher_user
        )
        module = Module.objects.create(
            course=course,
            title='Test Module',
            description='This is a test module.',
            order=1
        )
        ressource = Ressource.objects.create(
            module=module,
            title='Test Ressource',
            url='http://example.com/resource'
        )
        self.assertIn(ressource, module.ressources.all())

    def test_visio_link_display(self):
        course = Course.objects.create(
            title='Visio Course',
            description='This is a visio course.',
            teacher=self.teacher_user,
            visio_link='https://meet.google.com/xyz-abc-def'
        )
        self.client.login(username='student', password='password')
        course.students.add(self.student_user)
        response = self.client.get(reverse('users:student_course_detail', args=[course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'https://meet.google.com/xyz-abc-def')

    def test_visio_date_display(self):
        from datetime import datetime
        course = Course.objects.create(
            title='Visio Date Course',
            description='This is a visio date course.',
            teacher=self.teacher_user,
            visio_link='https://meet.google.com/xyz-abc-def',
            visio_date=datetime(2025, 12, 25, 10, 30, 0)
        )
        self.client.login(username='student', password='password')
        course.students.add(self.student_user)
        response = self.client.get(reverse('users:student_course_detail', args=[course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '25/12/2025 10:30')


class CourseFormTest(TestCase):
    def setUp(self):
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)

    def test_course_form_valid(self):
        form_data = {
            'title': 'New Course',
            'description': 'Description for new course',
            'teacher': self.teacher_user.id
        }
        form = CourseForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_course_form_invalid_missing_title(self):
        form_data = {
            'description': 'Description for new course',
            'teacher': self.teacher_user.id
        }
        form = CourseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_module_form_valid(self):
        form_data = {
            'title': 'New Module',
            'description': 'Description for new module',
            'order': 1
        }
        form = ModuleForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_module_form_invalid_missing_title(self):
        form_data = {
            'description': 'Description for new module',
            'order': 1
        }
        form = ModuleForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_ressource_form_valid_url(self):
        form_data = {
            'title': 'New Ressource',
            'url': 'http://example.com/new_resource'
        }
        form = RessourceForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_ressource_form_valid_file(self):
        # For file fields, you typically need to mock the file upload
        # This is a simplified test, a real test would use SimpleUploadedFile
        form_data = {
            'title': 'New Ressource File',
        }
        form = RessourceForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_ressource_form_invalid_missing_title(self):
        form_data = {
            'url': 'http://example.com/new_resource'
        }
        form = RessourceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_annonce_form_valid(self):
        form_data = {
            'titre': 'New Annonce',
            'contenu': 'Content for new annonce'
        }
        form = AnnonceForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_annonce_form_invalid_missing_titre(self):
        form_data = {
            'contenu': 'Content for new annonce'
        }
        form = AnnonceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('titre', form.errors)


class CourseAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='password', role=User.Role.ADMIN)
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.student_user = User.objects.create_user(username='student', email='student@example.com', password='password', role=User.Role.ETUDIANT)
        self.course = Course.objects.create(title='API Course', description='Desc', teacher=self.teacher_user)
        self.module = Module.objects.create(course=self.course, title='API Module', order=1)
        self.annonce = Annonce.objects.create(cours=self.course, titre='API Annonce', contenu='Content')

    def test_create_module_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('courses:api_create_module', args=[self.course.id]),
                                    json.dumps({'title': 'New API Module', 'description': 'New Desc', 'order': 2}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Module.objects.count(), 2)

    def test_update_module_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('courses:api_update_module', args=[self.module.id]),
                                    json.dumps({'title': 'Updated Module', 'description': 'Updated Desc', 'order': 1}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.module.refresh_from_db()
        self.assertEqual(self.module.title, 'Updated Module')

    def test_delete_module_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('courses:api_delete_module', args=[self.module.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Module.objects.count(), 0)

    def test_create_ressource_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('courses:api_create_ressource', args=[self.module.id]),
                                    {'title': 'New API Ressource', 'url': 'http://new.res/'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Ressource.objects.count(), 1)

    def test_update_ressource_api(self):
        ressource = Ressource.objects.create(module=self.module, title='Old Res', url='http://old.res/')
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('courses:api_update_ressource', args=[ressource.id]),
                                    {'title': 'Updated Res', 'url': 'http://updated.res/'})
        self.assertEqual(response.status_code, 200)
        ressource.refresh_from_db()
        self.assertEqual(ressource.title, 'Updated Res')

    def test_delete_ressource_api(self):
        ressource = Ressource.objects.create(module=self.module, title='To Delete', url='http://del.res/')
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('courses:api_delete_ressource', args=[ressource.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Ressource.objects.count(), 0)

    def test_create_annonce_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('courses:api_create_annonce', args=[self.course.id]),
                                    json.dumps({'titre': 'New API Annonce', 'contenu': 'New Content'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Annonce.objects.count(), 2)

    def test_update_annonce_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('courses:api_update_annonce', args=[self.annonce.id]),
                                    json.dumps({'titre': 'Updated Annonce', 'contenu': 'Updated Content'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.annonce.refresh_from_db()
        self.assertEqual(self.annonce.titre, 'Updated Annonce')

    def test_delete_annonce_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('courses:api_delete_annonce', args=[self.annonce.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Annonce.objects.count(), 0)

    def test_remove_student_from_course_api(self):
        self.course.students.add(self.student_user)
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('courses:api_remove_student_from_course', args=[self.course.id, self.student_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.student_user, self.course.students.all())

    def test_list_enrollable_students_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.get(reverse('courses:api_list_enrollable_students', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn({'id': self.student_user.id, 'name': f'{self.student_user.first_name} {self.student_user.last_name}', 'matricule': self.student_user.matricule}, data['students'])

    def test_enroll_student_api(self):
        self.client.login(username='teacher', password='password')
        response = self.client.post(reverse('courses:api_enroll_student', args=[self.course.id, self.student_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.student_user, self.course.students.all())

class CourseProgressTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher_user = User.objects.create_user(username='teacher', email='teacher@example.com', password='password', role=User.Role.ENSEIGNANT)
        self.student_user = User.objects.create_user(username='student', email='student@example.com', password='password', role=User.Role.ETUDIANT)
        self.course = Course.objects.create(title='Progress Course', description='Desc', teacher=self.teacher_user)
        self.module = Module.objects.create(course=self.course, title='Module 1', order=1)
        self.ressource = Ressource.objects.create(module=self.module, title='Ressource 1')
        self.course.students.add(self.student_user)

    def test_complete_ressource_api(self):
        self.client.login(username='student', password='password')
        response = self.client.post(reverse('courses:api_complete_ressource', args=[self.ressource.id]))
        self.assertEqual(response.status_code, 200)
        progress = CourseProgress.objects.get(student=self.student_user, course=self.course)
        self.assertIn(self.ressource, progress.completed_ressources.all())