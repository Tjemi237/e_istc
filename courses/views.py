from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from users.models import User
from .models import Course, Module, Ressource, Annonce, CourseProgress

from courses.forms import ModuleForm, RessourceForm, AnnonceForm
from administration.decorators import admin_required, course_owner_or_admin_required, module_owner_or_admin_required, ressource_owner_or_admin_required, annonce_owner_or_admin_required
import json
from django.contrib import messages

# API pour les modules

@module_owner_or_admin_required
@require_POST
def create_module(request, course_id):
    """Crée un module pour un cours spécifique.
    """
    course = Course.objects.get(pk=course_id)
    data = json.loads(request.body)
    form = ModuleForm(data)
    if form.is_valid():
        module = form.save(commit=False)
        module.course = course
        module.save()
        messages.success(request, 'Module créé avec succès !')
        return JsonResponse({'module': {
            'id': module.id,
            'title': module.title,
            'description': module.description,
            'order': module.order,
        }})
    else:
        messages.error(request, 'Erreur lors de la création du module.')
        return JsonResponse({'errors': form.errors}, status=400)

@module_owner_or_admin_required
def module_detail(request, module_id):
    try:
        module = Module.objects.get(pk=module_id)
        data = {
            'id': module.id,
            'title': module.title,
            'description': module.description,
            'order': module.order,
        }
        return JsonResponse(data)
    except Module.DoesNotExist:
        messages.error(request, 'Module non trouvé.')
        return JsonResponse({'error': 'Module non trouvé'}, status=404)

@module_owner_or_admin_required
@require_POST
def update_module(request, module_id):
    try:
        module = Module.objects.get(pk=module_id)
        data = json.loads(request.body)
        form = ModuleForm(data, instance=module)
        if form.is_valid():
            module = form.save()
            messages.success(request, 'Module mis à jour avec succès !')
            return JsonResponse({'module': {
                'id': module.id,
                'title': module.title,
                'description': module.description,
                'order': module.order,
            }})
        else:
            messages.error(request, 'Erreur lors de la mise à jour du module.')
            return JsonResponse({'errors': form.errors}, status=400)
    except Module.DoesNotExist:
        messages.error(request, 'Module non trouvé.')
        return JsonResponse({'message': 'Module non trouvé'}, status=404)

@module_owner_or_admin_required
@require_POST
def delete_module(request, module_id):
    try:
        module = Module.objects.get(pk=module_id)
        module.delete()
        messages.success(request, 'Module supprimé avec succès !')
        return JsonResponse({})
    except Module.DoesNotExist:
        messages.error(request, 'Module non trouvé.')
        return JsonResponse({'message': 'Module non trouvé'}, status=404)

# API pour les ressources

@ressource_owner_or_admin_required
@require_POST
def create_ressource(request, module_id):
    module = Module.objects.get(pk=module_id)
    form = RessourceForm(request.POST, request.FILES)
    if form.is_valid():
        ressource = form.save(commit=False)
        ressource.module = module
        ressource.save()
        messages.success(request, 'Ressource créée avec succès !')
        return JsonResponse({'ressource': {
            'id': ressource.id,
            'title': ressource.title,
            'file_url': ressource.file.url if ressource.file else None,
            'url': ressource.url,
        }})
    else:
        messages.error(request, 'Erreur lors de la création de la ressource.')
        return JsonResponse({'errors': form.errors}, status=400)

@ressource_owner_or_admin_required
def ressource_detail(request, ressource_id):
    try:
        ressource = Ressource.objects.get(pk=ressource_id)
        data = {
            'id': ressource.id,
            'title': ressource.title,
            'file': ressource.file.name if ressource.file else None,
            'url': ressource.url,
        }
        return JsonResponse(data)
    except Ressource.DoesNotExist:
        messages.error(request, 'Ressource non trouvée.')
        return JsonResponse({'error': 'Ressource non trouvée'}, status=404)

@ressource_owner_or_admin_required
@require_POST
def update_ressource(request, ressource_id):
    try:
        ressource = Ressource.objects.get(pk=ressource_id)
        form = RessourceForm(request.POST, request.FILES, instance=ressource)
        if form.is_valid():
            ressource = form.save()
            messages.success(request, 'Ressource mise à jour avec succès !')
            return JsonResponse({'ressource': {
                'id': ressource.id,
                'title': ressource.title,
                'file_url': ressource.file.url if ressource.file else None,
                'url': ressource.url,
            }})
        else:
            messages.error(request, 'Erreur lors de la mise à jour de la ressource.')
            return JsonResponse({'errors': form.errors}, status=400)
    except Ressource.DoesNotExist:
        messages.error(request, 'Ressource non trouvée.')
        return JsonResponse({'message': 'Ressource non trouvée'}, status=404)

@ressource_owner_or_admin_required
@require_POST
def delete_ressource(request, ressource_id):
    try:
        ressource = Ressource.objects.get(pk=ressource_id)
        ressource.delete()
        messages.success(request, 'Ressource supprimée avec succès !')
        return JsonResponse({})
    except Ressource.DoesNotExist:
        messages.error(request, 'Ressource non trouvée.')
        return JsonResponse({'message': 'Ressource non trouvée'}, status=404)

@course_owner_or_admin_required
@require_POST
def remove_student_from_course(request, course_id, student_id):
    try:
        course = Course.objects.get(pk=course_id)
        student = User.objects.get(pk=student_id)
        course.students.remove(student)
        messages.success(request, 'Étudiant retiré du cours avec succès !')
        return JsonResponse({})
    except (Course.DoesNotExist, User.DoesNotExist):
        messages.error(request, 'Cours ou étudiant non trouvé.')
        return JsonResponse({'message': 'Cours ou étudiant non trouvé.'}, status=404)

# API pour les annonces

@course_owner_or_admin_required
@require_POST
def create_annonce(request, course_id):
    course = Course.objects.get(pk=course_id)
    data = json.loads(request.body)
    form = AnnonceForm(data)
    if form.is_valid():
        annonce = form.save(commit=False)
        annonce.cours = course
        annonce.save()
        messages.success(request, 'Annonce créée avec succès !')
        return JsonResponse({'annonce': {
            'id': annonce.id,
            'titre': annonce.titre,
            'contenu': annonce.contenu,
            'cree_le': annonce.cree_le.strftime('%d/%m/%Y %H:%M'),
        }})
    else:
        messages.error(request, 'Erreur lors de la création de l\'annonce.')
        return JsonResponse({'errors': form.errors}, status=400)

@annonce_owner_or_admin_required
def annonce_detail(request, annonce_id):
    try:
        annonce = Annonce.objects.get(pk=annonce_id)
        data = {
            'id': annonce.id,
            'titre': annonce.titre,
            'contenu': annonce.contenu,
        }
        return JsonResponse(data)
    except Annonce.DoesNotExist:
        messages.error(request, 'Annonce non trouvée.')
        return JsonResponse({'error': 'Annonce non trouvée'}, status=404)

@annonce_owner_or_admin_required
@require_POST
def update_annonce(request, annonce_id):
    try:
        annonce = Annonce.objects.get(pk=annonce_id)
        data = json.loads(request.body)
        form = AnnonceForm(data, instance=annonce)
        if form.is_valid():
            annonce = form.save()
            messages.success(request, 'Annonce mise à jour avec succès !')
            return JsonResponse({'annonce': {
                'id': annonce.id,
                'titre': annonce.titre,
                'contenu': annonce.contenu,
                'cree_le': annonce.cree_le.strftime('%d/%m/%Y %H:%M'),
            }})
        else:
            messages.error(request, 'Erreur lors de la mise à jour de l\'annonce.')
            return JsonResponse({'errors': form.errors}, status=400)
    except Annonce.DoesNotExist:
        messages.error(request, 'Annonce non trouvée.')
        return JsonResponse({'message': 'Annonce non trouvée'}, status=404)

@annonce_owner_or_admin_required
@require_POST
def delete_annonce(request, annonce_id):
    try:
        annonce = Annonce.objects.get(pk=annonce_id)
        annonce.delete()
        messages.success(request, 'Annonce supprimée avec succès !')
        return JsonResponse({})
    except Annonce.DoesNotExist:
        messages.error(request, 'Annonce non trouvée.')
        return JsonResponse({'message': 'Annonce non trouvée'}, status=404)

@course_owner_or_admin_required
def list_enrollable_students(request, course_id):
    course = Course.objects.get(pk=course_id)
    enrolled_student_ids = course.students.values_list('id', flat=True)
    enrollable_students = User.objects.filter(role=User.Role.ETUDIANT).exclude(id__in=enrolled_student_ids)
    students_data = [
        {
            'id': student.id,
            'name': f'{student.first_name} {student.last_name}',
            'matricule': student.matricule
        } for student in enrollable_students
    ]
    return JsonResponse({'students': students_data})

@course_owner_or_admin_required
@require_POST
def enroll_student(request, course_id, student_id):
    try:
        course = Course.objects.get(pk=course_id)
        student = User.objects.get(pk=student_id, role=User.Role.ETUDIANT)
        course.students.add(student)
        return JsonResponse({'status': 'success', 'student': {
            'id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'email': student.email,
            'matricule': student.matricule
        }, 'message': 'Étudiant inscrit avec succès !'})
    except (Course.DoesNotExist, User.DoesNotExist):
        return JsonResponse({'status': 'error', 'message': 'Cours ou étudiant non trouvé.'}, status=404)

@require_POST
@login_required
def complete_ressource(request, ressource_id):
    ressource = get_object_or_404(Ressource, pk=ressource_id)
    course = ressource.module.course
    progress, created = CourseProgress.objects.get_or_create(student=request.user, course=course)
    progress.completed_ressources.add(ressource)
    return JsonResponse({'status': 'success'})
