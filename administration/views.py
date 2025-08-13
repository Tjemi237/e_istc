from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from users.models import User
from users.forms import CustomUserCreationForm, CustomUserChangeForm
from courses.models import Course, Module, Ressource, Category, CourseProgress
from courses.forms import CourseForm, ModuleForm, RessourceForm, CategoryForm
from django.db.models import Avg, Count
from evaluations.models import Activite, Soumission, Tentative
from .decorators import admin_required, course_owner_or_admin_required
import json
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify

@admin_required
def user_management_page(request):
    users = User.objects.all().order_by('last_name')
    return render(request, 'administration/user_management.html', {'users': users})

@admin_required
def course_management_page(request):
    courses = Course.objects.all().order_by('-created_at')
    teachers = User.objects.filter(role=User.Role.ENSEIGNANT)
    categories = Category.objects.all().order_by('name')
    return render(request, 'administration/course_management.html', {'courses': courses, 'teachers': teachers, 'categories': categories})

@course_owner_or_admin_required
def course_detail_page(request, course_id):
    course = Course.objects.get(pk=course_id)
    enrolled_students = course.students.all()
    activites = course.activites.all().order_by('-created_at')
    annonces = course.annonces.all()
    context = {
        'course': course,
        'enrolled_students': enrolled_students,
        'activites': activites,
        'annonces': annonces,
    }
    return render(request, 'administration/course_detail_page.html', context)

@admin_required
@require_POST
def create_user(request):
    form = CustomUserCreationForm(request.POST, request.FILES)
    if form.is_valid():
        user = form.save()
        # Log the action
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(user).pk,
            object_id=user.pk,
            object_repr=str(user),
            action_flag=ADDITION,
            change_message=f'Utilisateur {user.username} créé.'
        )
        user_data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role,
            'get_role_display': user.get_role_display(),
            'matricule': user.matricule,
            'specialite': user.specialite,
            'is_locked': user.is_locked,
        }
        return JsonResponse({'status': 'success', 'user': user_data, 'message': 'Utilisateur créé avec succès !'})
    else:
        return JsonResponse({'status': 'error', 'errors': form.errors, 'message': "Erreur lors de la création de l'utilisateur."}, status=400)

@admin_required
def user_detail(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'role': user.role,
            'matricule': user.matricule,
            'specialite': user.specialite,
        }
        return JsonResponse(data)
    except User.DoesNotExist:
        messages.error(request, 'Utilisateur non trouvé.')
        return JsonResponse({'error': 'Utilisateur non trouvé'}, status=404)

@admin_required
@require_POST
def update_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save()
            # Log the action
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(user).pk,
                object_id=user.pk,
                object_repr=str(user),
                action_flag=CHANGE,
                change_message=f'Utilisateur {user.username} mis à jour.'
            )
            user_data = {
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': user.role,
                'get_role_display': user.get_role_display(),
                'matricule': user.matricule,
                'specialite': user.specialite,
                'is_locked': user.is_locked,
            }
            return JsonResponse({'status': 'success', 'user': user_data, 'message': 'Utilisateur mis à jour avec succès !'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors, 'message': "Erreur lors de la mise à jour de l'utilisateur."}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Utilisateur non trouvé'}, status=404)


@admin_required
@require_POST
def delete_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        # Log the action before deletion
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(user).pk,
            object_id=user.pk,
            object_repr=str(user),
            action_flag=DELETION,
            change_message=f'Utilisateur {user.username} supprimé.'
        )
        user.delete()
        return JsonResponse({'status': 'success', 'message': 'Utilisateur supprimé avec succès !'})
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Utilisateur non trouvé'}, status=404)

# API pour les cours

@admin_required
@require_POST
def create_course(request):
    form = CourseForm(request.POST, request.FILES)
    if form.is_valid():
        course = form.save()
        # Log the action
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(course).pk,
            object_id=course.pk,
            object_repr=str(course),
            action_flag=ADDITION,
            change_message=f'Cours {course.title} créé.'
        )
        course_data = {
            'id': course.id,
            'title': course.title,
            'teacher': {
                'id': course.teacher.id,
                'name': f'{course.teacher.first_name} {course.teacher.last_name}'
            },
            'created_at': course.created_at.strftime('%d/%m/%Y')
        }
        messages.success(request, 'Cours créé avec succès !')
        return JsonResponse({'status': 'success', 'course': course_data})
    else:
        messages.error(request, 'Erreur lors de la création du cours.')
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@admin_required
def course_detail(request, course_id):
    try:
        course = Course.objects.get(pk=course_id)
        data = {
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'teacher_id': course.teacher.id
        }
        return JsonResponse(data)
    except Course.DoesNotExist:
        messages.error(request, 'Cours non trouvé.')
        return JsonResponse({'error': 'Cours non trouvé'}, status=404)

@admin_required
@require_POST
def update_course(request, course_id):
    try:
        course = Course.objects.get(pk=course_id)
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            course = form.save()
            # Log the action
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(course).pk,
                object_id=course.pk,
                object_repr=str(course),
                action_flag=CHANGE,
                change_message=f'Cours {course.title} mis à jour.'
            )
            course_data = {
                'id': course.id,
                'title': course.title,
                'teacher': {
                    'id': course.teacher.id,
                    'name': f'{course.teacher.first_name} {course.teacher.last_name}'
                },
                'created_at': course.created_at.strftime('%d/%m/%Y')
            }
            messages.success(request, 'Cours mis à jour avec succès !')
            return JsonResponse({'status': 'success', 'course': course_data})
        else:
            messages.error(request, 'Erreur lors de la mise à jour du cours.')
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    except Course.DoesNotExist:
        messages.error(request, 'Cours non trouvé.')
        return JsonResponse({'status': 'error', 'message': 'Cours non trouvé'}, status=404)

@admin_required
@require_POST
def delete_course(request, course_id):
    try:
        course = Course.objects.get(pk=course_id)
        # Log the action before deletion
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(course).pk,
            object_id=course.pk,
            object_repr=str(course),
            action_flag=DELETION,
            change_message=f'Cours {course.title} supprimé.'
        )
        course.delete()
        messages.success(request, 'Cours supprimé avec succès !')
        return JsonResponse({'status': 'success'})
    except Course.DoesNotExist:
        messages.error(request, 'Cours non trouvé.')
        return JsonResponse({'status': 'error', 'message': 'Cours non trouvé'}, status=404)

@admin_required
@require_POST
def lock_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_locked = True
    user.save()
    # Log the action
    LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=ContentType.objects.get_for_model(user).pk,
        object_id=user.pk,
        object_repr=str(user),
        action_flag=CHANGE,
        change_message=f'Utilisateur {user.username} verrouillé.'
    )
    return JsonResponse({'status': 'success', 'message': "L'utilisateur a été verrouillé."})

@admin_required
@require_POST
def unlock_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_locked = False
    user.save()
    # Log the action
    LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=ContentType.objects.get_for_model(user).pk,
        object_id=user.pk,
        object_repr=str(user),
        action_flag=CHANGE,
        change_message=f'Utilisateur {user.username} déverrouillé.'
    )
    return JsonResponse({'status': 'success', 'message': "L'utilisateur a été déverrouillé."})

@admin_required
def course_progress_view(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    students = course.students.all()
    progress_data = []
    for student in students:
        progress, created = CourseProgress.objects.get_or_create(student=student, course=course)
        total_ressources = Ressource.objects.filter(module__course=course).count()
        completed_ressources = progress.completed_ressources.count()
        progress_percentage = (completed_ressources / total_ressources) * 100 if total_ressources > 0 else 0
        progress_data.append({
            'student': student,
            'progress': progress_percentage,
            'completed_ressources': completed_ressources,
            'total_ressources': total_ressources
        })
    return render(request, 'administration/course_progress.html', {'course': course, 'progress_data': progress_data})

@admin_required
def category_management_page(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'administration/category_management.html', {'categories': categories})

@admin_required
@require_POST
def create_category(request):
    form = CategoryForm(request.POST, request.FILES)
    if form.is_valid():
        category = form.save(commit=False)
        category.slug = slugify(category.name)
        category.save()
        # Log the action
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(category).pk,
            object_id=category.pk,
            object_repr=str(category),
            action_flag=ADDITION,
            change_message=f'Catégorie {category.name} créée.'
        )
        category_data = {
            'id': category.id,
            'name': category.name,
            'slug': category.slug
        }
        messages.success(request, 'Catégorie créée avec succès !')
        return JsonResponse({'status': 'success', 'category': category_data})
    else:
        messages.error(request, 'Erreur lors de la création de la catégorie.')
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@admin_required
def category_detail(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
        data = {
            'id': category.id,
            'name': category.name,
            'slug': category.slug
        }
        return JsonResponse(data)
    except Category.DoesNotExist:
        messages.error(request, 'Catégorie non trouvée.')
        return JsonResponse({'error': 'Catégorie non trouvée'}, status=404)

@admin_required
@require_POST
def update_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save()
            # Log the action
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(category).pk,
                object_id=category.pk,
                object_repr=str(category),
                action_flag=CHANGE,
                change_message=f'Catégorie {category.name} mise à jour.'
            )
            category_data = {
                'id': category.id,
                'name': category.name,
                'slug': category.slug
            }
            messages.success(request, 'Catégorie mise à jour avec succès !')
            return JsonResponse({'status': 'success', 'category': category_data})
        else:
            messages.error(request, 'Erreur lors de la mise à jour de la catégorie.')
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    except Category.DoesNotExist:
        messages.error(request, 'Catégorie non trouvée.')
        return JsonResponse({'status': 'error', 'message': 'Catégorie non trouvée'}, status=404)

@admin_required
def reports_page(request):
    courses = Course.objects.all()
    reports = []
    for course in courses:
        student_count = course.students.count()
        assignment_count = Activite.objects.filter(course=course, activity_type='DEVOIR').count()
        quiz_count = Activite.objects.filter(course=course, activity_type='QUIZ').count()
        avg_assignment_grade = Soumission.objects.filter(activite__course=course).aggregate(Avg('note'))['note__avg'] or 0
        avg_quiz_score = Tentative.objects.filter(activite__course=course).aggregate(Avg('score'))['score__avg'] or 0
        
        reports.append({
            'course': course,
            'student_count': student_count,
            'assignment_count': assignment_count,
            'quiz_count': quiz_count,
            'avg_assignment_grade': avg_assignment_grade,
            'avg_quiz_score': avg_quiz_score
        })

    # Global statistics
    total_users = User.objects.count()
    total_students = User.objects.filter(role=User.Role.ETUDIANT).count()
    total_teachers = User.objects.filter(role=User.Role.ENSEIGNANT).count()
    total_courses = Course.objects.count()
    total_enrollments = User.objects.filter(role=User.Role.ETUDIANT).aggregate(Count('courses'))['courses__count']
    
    context = {
        'reports': reports,
        'total_users': total_users,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
    }
    return render(request, 'administration/reports.html', context)

@admin_required
def audit_logs_page(request):
    logs = LogEntry.objects.all().order_by('-action_time')[:100] # Get last 100 logs
    return render(request, 'administration/audit_logs.html', {'logs': logs})

@admin_required
@require_POST
def delete_category(request, category_id):
    try:
        category = Category.objects.get(pk=category_id)
        # Log the action before deletion
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(category).pk,
            object_id=category.pk,
            object_repr=str(category),
            action_flag=DELETION,
            change_message=f'Catégorie {category.name} supprimée.'
        )
        category.delete()
        return JsonResponse({'status': 'success', 'message': 'Catégorie supprimée avec succès !'})
    except Category.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Catégorie non trouvée.'}, status=404)