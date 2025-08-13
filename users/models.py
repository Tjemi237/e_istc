from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        ENSEIGNANT = "ENSEIGNANT", "Enseignant"
        ETUDIANT = "ETUDIANT", "Etudiant"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.ETUDIANT)
    photo = models.ImageField(upload_to='users/photos/', null=True, blank=True, verbose_name="Photo de profil")
    matricule = models.CharField(max_length=254, unique=True, null=True, blank=True)
    specialite = models.CharField(max_length=254, null=True, blank=True)
    niveau_etude = models.CharField(max_length=100, null=True, blank=True, verbose_name="Niveau d'étude")
    filiere = models.CharField(max_length=100, null=True, blank=True, verbose_name="Filière")
    statut_enseignant = models.CharField(max_length=100, null=True, blank=True, verbose_name="Statut Enseignant")
    courses = models.ManyToManyField('courses.Course', related_name='students', blank=True)
    is_locked = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.role != self.Role.ETUDIANT:
            self.matricule = None
        if self.role != self.Role.ENSEIGNANT:
            self.specialite = None
        super().save(*args, **kwargs)

    @property
    def is_etudiant(self):
        return self.role == self.Role.ETUDIANT

    @property
    def is_enseignant(self):
        return self.role == self.Role.ENSEIGNANT

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created and instance.email:
        try:
            # Générer le lien de réinitialisation de mot de passe
            token = default_token_generator.make_token(instance)
            uid = urlsafe_base64_encode(force_bytes(instance.pk))
            reset_link = f"http://localhost:8000{reverse('users:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})}"

            # Déterminer l'identifiant
            identifier = instance.matricule if instance.role == User.Role.ETUDIANT else instance.username

            # Rendre le template de l'e-mail
            mail_subject = 'Bienvenue sur la plateforme E-ISTC !'
            message = render_to_string('users/email/bienvenue.html', {
                'user': instance,
                'identifier': identifier,
                'reset_link': reset_link,
            })
            send_mail(mail_subject, message, 'no-reply@istc.ci', [instance.email], html_message=message)
            logger.info(f"E-mail de bienvenue envoyé à {instance.email} (ID: {instance.id})")
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'e-mail de bienvenue à {instance.email} (ID: {instance.id}): {e}")