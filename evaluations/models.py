from django.db import models
from courses.models import Course
from users.models import User

class Activite(models.Model):
    class ActivityType(models.TextChoices):
        DEVOIR = 'DEVOIR', 'Devoir'
        QUIZ = 'QUIZ', 'Quiz'
        SONDAGE = 'SONDAGE', 'Sondage'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='activites')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    activity_type = models.CharField(max_length=10, choices=ActivityType.choices)
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    class QuestionType(models.TextChoices):
        CHOIX_UNIQUE = 'UNIQUE', 'Choix Unique'
        CHOIX_MULTIPLE = 'MULTIPLE', 'Choix Multiple'

    activite = models.ForeignKey(Activite, on_delete=models.CASCADE, related_name='questions', limit_choices_to={'activity_type': 'QUIZ'})
    intitule = models.TextField()
    type_question = models.CharField(max_length=10, choices=QuestionType.choices, default=QuestionType.CHOIX_UNIQUE)

    def __str__(self):
        return self.intitule

class Choix(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choix')
    texte = models.CharField(max_length=255)
    est_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.texte

class Soumission(models.Model):
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE, related_name='soumissions', limit_choices_to={'activity_type': 'DEVOIR'})
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='soumissions')
    fichier = models.FileField(upload_to='soumissions/%Y/%m/%d/')
    date_soumission = models.DateTimeField(auto_now_add=True)
    note = models.FloatField(null=True, blank=True)
    commentaires_enseignant = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('activite', 'etudiant')

class Tentative(models.Model):
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE, related_name='tentatives', limit_choices_to={'activity_type': 'QUIZ'})
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tentatives')
    score = models.FloatField()
    date_tentative = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('activite', 'etudiant')

class QuestionSondage(models.Model):
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE, related_name='questions_sondage', limit_choices_to={'activity_type': 'SONDAGE'})
    intitule = models.TextField()

    def __str__(self):
        return self.intitule

class ReponseSondage(models.Model):
    question = models.ForeignKey(QuestionSondage, on_delete=models.CASCADE, related_name='reponses')
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reponses_sondage')
    reponse = models.TextField()

    class Meta:
        unique_together = ('question', 'etudiant')