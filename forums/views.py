from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.decorators.http import require_POST
from courses.models import Course
from .models import SujetDiscussion, MessageForum
from .forms import SujetForm, MessageForm
from users.models import User
from django.contrib import messages

def check_user_permission_for_course(user, course):
    """
    Vérifie si l'utilisateur a la permission de voir le contenu d'un cours.
    (Admin, enseignant du cours, ou étudiant inscrit)
    """
    if user.role == User.Role.ADMIN or course.teacher == user or user in course.students.all():
        return True
    return False

@login_required
def forum_cours(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if not check_user_permission_for_course(request.user, course):
        raise PermissionDenied

    sujets = SujetDiscussion.objects.filter(cours=course)
    context = {
        'course': course,
        'sujets': sujets,
    }
    return render(request, 'forums/forum_cours.html', context)

@login_required
def details_sujet(request, sujet_id):
    sujet = get_object_or_404(SujetDiscussion, pk=sujet_id)
    course = sujet.cours
    if not check_user_permission_for_course(request.user, course):
        raise PermissionDenied

    if request.method == 'POST':
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.sujet = sujet
            message.auteur = request.user
            message.save()
            messages.success(request, 'Message envoyé avec succès !')
            return redirect('forums:details_sujet', sujet_id=sujet.id)
        else:
            messages.error(request, 'Erreur lors de l\'envoi du message.')
    else:
        message_form = MessageForm()

    messages_list = sujet.messages.all()
    context = {
        'sujet': sujet,
        'course': course,
        'messages': messages_list,
        'message_form': message_form,
    }
    return render(request, 'forums/details_sujet.html', context)

@login_required
def creer_sujet(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if not check_user_permission_for_course(request.user, course):
        raise PermissionDenied

    if request.method == 'POST':
        sujet_form = SujetForm(request.POST)
        message_form = MessageForm(request.POST)
        if sujet_form.is_valid() and message_form.is_valid():
            sujet = sujet_form.save(commit=False)
            sujet.cours = course
            sujet.auteur = request.user
            sujet.save()

            message = message_form.save(commit=False)
            message.sujet = sujet
            message.auteur = request.user
            message.save()
            messages.success(request, 'Sujet de discussion créé avec succès !')
            return redirect('forums:details_sujet', sujet_id=sujet.id)
        else:
            messages.error(request, 'Erreur lors de la création du sujet.')
    else:
        sujet_form = SujetForm()
        message_form = MessageForm()

    context = {
        'course': course,
        'sujet_form': sujet_form,
        'message_form': message_form,
    }
    return render(request, 'forums/creer_sujet.html', context)

@login_required
@require_POST
def ajouter_message(request, sujet_id):
    sujet = get_object_or_404(SujetDiscussion, pk=sujet_id)
    if not check_user_permission_for_course(request.user, sujet.cours):
        raise PermissionDenied

    form = MessageForm(request.POST)
    if form.is_valid():
        message = form.save(commit=False)
        message.sujet = sujet
        message.auteur = request.user
        message.save()
        messages.success(request, 'Message ajouté avec succès !')
    else:
        messages.error(request, 'Erreur lors de l\'ajout du message.')
    return redirect('forums:details_sujet', sujet_id=sujet.id)


@login_required
@require_POST
def supprimer_message(request, message_id):
    message = get_object_or_404(MessageForum, pk=message_id)
    sujet = message.sujet
    # Seul l'auteur, l'enseignant du cours ou un admin peut supprimer
    if request.user == message.auteur or request.user == sujet.cours.teacher or request.user.role == User.Role.ADMIN:
        message.delete()
        messages.success(request, 'Message supprimé avec succès !')
        # Si c'était le premier message, on supprime le sujet aussi
        if not sujet.messages.exists():
            sujet.delete()
            messages.success(request, 'Sujet de discussion supprimé car il ne contenait plus de messages.')
            return redirect('forums:forum_cours', course_id=sujet.cours.id)
        return redirect('forums:details_sujet', sujet_id=sujet.id)
    else:
        messages.error(request, 'Vous n\'avez pas la permission de supprimer ce message.')
        raise PermissionDenied

@login_required
@require_POST
def supprimer_sujet(request, sujet_id):
    sujet = get_object_or_404(SujetDiscussion, pk=sujet_id)
    course_id = sujet.cours.id
    # Seul l'auteur du sujet, l'enseignant du cours ou un admin peut supprimer
    if request.user == sujet.auteur or request.user == sujet.cours.teacher or request.user.role == User.Role.ADMIN:
        sujet.delete()
        messages.success(request, 'Sujet de discussion supprimé avec succès !')
        return redirect('forums:forum_cours', course_id=course_id)
    else:
        messages.error(request, 'Vous n\'avez pas la permission de supprimer ce sujet.')
        raise PermissionDenied
