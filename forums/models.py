from django.db import models
from courses.models import Course
from users.models import User

class SujetDiscussion(models.Model):
    """
    Représente un sujet de discussion (un fil ou "topic") dans le forum d'un cours.
    """
    cours = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sujets_forum')
    titre = models.CharField(max_length=255)
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sujets_crees')
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre

    class Meta:
        ordering = ['-mis_a_jour_le']

class MessageForum(models.Model):
    """
    Représente un message (une réponse) posté dans un sujet de discussion.
    """
    sujet = models.ForeignKey(SujetDiscussion, on_delete=models.CASCADE, related_name='messages')
    auteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_forum')
    contenu = models.TextField()
    cree_le = models.DateTimeField(auto_now_add=True)
    mis_a_jour_le = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Réponse de {self.auteur} sur '{self.sujet.titre}'"

    class Meta:
        ordering = ['cree_le']