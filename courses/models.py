from django.db import models
from users.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.ImageField(upload_to='categories/icons/', null=True, blank=True, verbose_name="Icône")

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='courses/images/', null=True, blank=True, verbose_name="Image d'illustration")
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.ENSEIGNANT})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    visio_link = models.URLField(blank=True, null=True)
    visio_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

class CourseProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progress')
    completed_ressources = models.ManyToManyField('Ressource', blank=True)

    class Meta:
        unique_together = ('student', 'course')

class Annonce(models.Model):
    cours = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='annonces')
    titre = models.CharField(max_length=255)
    contenu = models.TextField()
    cree_le = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre

    class Meta:
        ordering = ['-cree_le']

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.course.title} - {self.title}'

class Ressource(models.Model):
    module = models.ForeignKey(Module, related_name='ressources', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='ressources/%Y/%m/%d/', blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title