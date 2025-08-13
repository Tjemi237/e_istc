from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from courses.models import Annonce, Course
from evaluations.models import Activite
from messaging.models import Message
from .models import Notification

@receiver(post_save, sender=Annonce)
def create_annonce_notification(sender, instance, created, **kwargs):
    if created:
        for student in instance.cours.students.all():
            Notification.objects.create(
                user=student,
                message=f"Nouvelle annonce dans le cours {instance.cours.title}: {instance.titre}",
                link=reverse('users:student_course_detail', args=[instance.cours.id])
            )

@receiver(post_save, sender=Activite)
def create_activite_notification(sender, instance, created, **kwargs):
    if created:
        for student in instance.course.students.all():
            Notification.objects.create(
                user=student,
                message=f"Nouvelle évaluation dans le cours {instance.course.title}: {instance.title}",
                link=reverse('users:student_course_detail', args=[instance.course.id])
            )

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if created:
        for participant in instance.conversation.participants.all():
            if participant != instance.sender:
                Notification.objects.create(
                    user=participant,
                    message=f"Nouveau message de {instance.sender.first_name} {instance.sender.last_name}",
                    link=reverse('messaging:conversation_detail', args=[instance.conversation.id])
                )

@receiver(post_save, sender=Course)
def create_visio_notification(sender, instance, created, **kwargs):
    if not created and (instance.visio_link or instance.visio_date):
        # Check if visio_link or visio_date actually changed
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return # Object didn't exist before, so it's a new creation, not an update of visio info

        if old_instance.visio_link != instance.visio_link or old_instance.visio_date != instance.visio_date:
            message_text = f"Une visioconférence a été planifiée/mise à jour pour le cours {instance.title}."
            if instance.visio_date:
                message_text += f" Date: {instance.visio_date.strftime('%d/%m/%Y %H:%M')}."
            if instance.visio_link:
                message_text += f" Lien: {instance.visio_link}"

            for student in instance.students.all():
                Notification.objects.create(
                    user=student,
                    message=message_text,
                    link=reverse('users:student_course_detail', args=[instance.id])
                )
