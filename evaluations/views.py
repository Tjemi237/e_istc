from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from courses.models import Course
from .models import Activite, Question, Choix, Soumission, QuestionSondage, ReponseSondage
from .forms import ActiviteForm, QuestionForm, ChoixForm, QuestionSondageForm, ReponseSondageForm
from administration.decorators import course_owner_or_admin_required
from .decorators import activity_owner_or_admin_required, question_owner_or_admin_required, submission_owner_or_admin_required, sondage_participant_required
import json
from django.contrib import messages

@course_owner_or_admin_required
@require_POST
def create_activity(request, course_id):
    course = Course.objects.get(pk=course_id)
    data = json.loads(request.body)
    form = ActiviteForm(data)
    if form.is_valid():
        activite = form.save(commit=False)
        activite.course = course
        activite.save()
        messages.success(request, 'Activité créée avec succès !')
        activite_data = {
            'id': activite.id,
            'title': activite.title,
            'description': activite.description,
            'activity_type': activite.get_activity_type_display(),
            'due_date': activite.due_date.isoformat() if activite.due_date else None,
        }
        messages.success(request, 'Activité créée avec succès !')
        return JsonResponse({'activite': activite_data})
    else:
        messages.error(request, 'Erreur lors de la création de l\'activité.')
        return JsonResponse({'errors': form.errors}, status=400)

@activity_owner_or_admin_required
def activity_detail(request, activity_id):
    try:
        activite = Activite.objects.get(pk=activity_id)
        data = {
            'id': activite.id,
            'title': activite.title,
            'description': activite.description,
            'activity_type': activite.activity_type,
            'due_date': activite.due_date.isoformat() if activite.due_date else None,
        }
        return JsonResponse(data)
    except Activite.DoesNotExist:
        messages.error(request, 'Activité non trouvée.')
        return JsonResponse({'error': 'Activité non trouvée'}, status=404)

@activity_owner_or_admin_required
@require_POST
def update_activity(request, activity_id):
    try:
        activite = Activite.objects.get(pk=activity_id)
        data = json.loads(request.body)
        form = ActiviteForm(data, instance=activite)
        if form.is_valid():
            activite = form.save()
            messages.success(request, 'Activité mise à jour avec succès !')
            activite_data = {
                'id': activite.id,
                'title': activite.title,
                'description': activite.description,
                'activity_type': activite.get_activity_type_display(),
                'due_date': activite.due_date.isoformat() if activite.due_date else None,
            }
            messages.success(request, 'Activité mise à jour avec succès !')
            return JsonResponse({'activite': activite_data})
        else:
            messages.error(request, 'Erreur lors de la mise à jour de l\'activité.')
            return JsonResponse({'errors': form.errors}, status=400)
    except Activite.DoesNotExist:
        messages.error(request, 'Activité non trouvée.')
        return JsonResponse({'message': 'Activité non trouvée'}, status=404)

@activity_owner_or_admin_required
@require_POST
def delete_activity(request, activity_id):
    try:
        activite = Activite.objects.get(pk=activity_id)
        activite.delete()
        messages.success(request, 'Activité supprimée avec succès !')
        messages.success(request, 'Activité supprimée avec succès !')
        return JsonResponse({})
    except Activite.DoesNotExist:
        messages.error(request, 'Activité non trouvée.')
        return JsonResponse({'message': 'Activité non trouvée'}, status=404)

# API pour les questions

@activity_owner_or_admin_required
def list_questions(request, quiz_id):
    questions = Question.objects.filter(activite_id=quiz_id)
    data = {
        'questions': [
            {
                'id': q.id,
                'intitule': q.intitule,
            } for q in questions
        ]
    }
    return JsonResponse(data)

@question_owner_or_admin_required
def question_detail(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
        choix = question.choix.all()
        data = {
            'id': question.id,
            'intitule': question.intitule,
            'type_question': question.type_question,
            'choix': [
                {
                    'id': c.id,
                    'texte': c.texte,
                    'est_correct': c.est_correct
                } for c in choix
            ]
        }
        return JsonResponse(data)
    except Question.DoesNotExist:
        messages.error(request, 'Question non trouvée.')
        return JsonResponse({'error': 'Question non trouvée'}, status=404)

@activity_owner_or_admin_required
@require_POST
def create_question(request, quiz_id):
    activite = Activite.objects.get(pk=quiz_id)
    data = json.loads(request.body)
    question = Question.objects.create(
        activite=activite,
        intitule=data['intitule'],
        type_question=data['type_question']
    )
    for choice_data in data['choices']:
        Choix.objects.create(
            question=question,
            texte=choice_data['text'],
            est_correct=choice_data['is_correct']
        )
    messages.success(request, 'Question créée avec succès !')
    return JsonResponse({})

@question_owner_or_admin_required
@require_POST
def update_question(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
        data = json.loads(request.body)
        question.intitule = data['intitule']
        question.type_question = data['type_question']
        question.save()
        question.choix.all().delete()
        for choice_data in data['choices']:
            Choix.objects.create(
                question=question,
                texte=choice_data['text'],
                est_correct=choice_data['is_correct']
            )
        messages.success(request, 'Question mise à jour avec succès !')
        return JsonResponse({})
    except Question.DoesNotExist:
        messages.error(request, 'Question non trouvée.')
        return JsonResponse({'message': 'Question non trouvée'}, status=404)

@question_owner_or_admin_required
@require_POST
def delete_question(request, question_id):
    try:
        question = Question.objects.get(pk=question_id)
        question.delete()
        messages.success(request, 'Question supprimée avec succès !')
        return JsonResponse({})
    except Question.DoesNotExist:
        messages.error(request, 'Question non trouvée.')
        return JsonResponse({'message': 'Question non trouvée'}, status=404)

# API pour la notation des devoirs

@activity_owner_or_admin_required
def list_submissions(request, activity_id):
    activite = Activite.objects.get(pk=activity_id)
    soumissions = Soumission.objects.filter(activite=activite).select_related('etudiant')
    data = {
        'soumissions': [
            {
                'id': s.id,
                'etudiant_name': f'{s.etudiant.first_name} {s.etudiant.last_name}',
                'file_url': s.fichier.url if s.fichier else None,
                'date_soumission': s.date_soumission.isoformat(),
                'note': s.note
            } for s in soumissions
        ]
    }
    return JsonResponse(data)

@submission_owner_or_admin_required
@require_POST
def grade_submission(request, submission_id):
    try:
        soumission = Soumission.objects.get(pk=submission_id)
        data = json.loads(request.body)
        note = data.get('note')
        commentaires = data.get('commentaires_enseignant', '')
        if note is not None:
            soumission.note = float(note)
            soumission.commentaires_enseignant = commentaires
            soumission.save()
            messages.success(request, 'Note et commentaires enregistrés avec succès !')
            return JsonResponse({})
        else:
            messages.error(request, 'Note manquante.')
            return JsonResponse({'message': 'Note manquante.'}, status=400)
    except Soumission.DoesNotExist:
        messages.error(request, 'Soumission non trouvée.')
        return JsonResponse({'message': 'Soumission non trouvée'}, status=404)

@activity_owner_or_admin_required
def sondage_results(request, activity_id):
    activite = get_object_or_404(Activite, pk=activity_id, activity_type='SONDAGE')
    questions = activite.questions_sondage.all()
    
    results = []
    for question in questions:
        responses = ReponseSondage.objects.filter(question=question).order_by('etudiant__last_name', 'etudiant__first_name')
        results.append({
            'question': question.intitule,
            'total_responses': responses.count(),
            'individual_responses': [{
                'etudiant_name': f'{r.etudiant.first_name} {r.etudiant.last_name}',
                'reponse': r.reponse
            } for r in responses]
        })

    return render(request, 'evaluations/sondage_results.html', {'activite': activite, 'results': results})

# API pour les sondages

@activity_owner_or_admin_required
@require_POST
def create_sondage_question(request, activity_id):
    activite = get_object_or_404(Activite, pk=activity_id, activity_type='SONDAGE')
    data = json.loads(request.body)
    form = QuestionSondageForm(data)
    if form.is_valid():
        question = form.save(commit=False)
        question.activite = activite
        question.save()
        messages.success(request, 'Question de sondage créée avec succès !')
        return JsonResponse({'question': {'id': question.id, 'intitule': question.intitule}})
    else:
        messages.error(request, 'Erreur lors de la création de la question de sondage.')
        return JsonResponse({'errors': form.errors}, status=400)

@sondage_participant_required
@require_POST
def submit_sondage_response(request, question_id):
    question = get_object_or_404(QuestionSondage, pk=question_id)
    data = json.loads(request.body)
    
    # Check if student already responded to this question
    if ReponseSondage.objects.filter(question=question, etudiant=request.user).exists():
        return JsonResponse({'status': 'error', 'message': 'Vous avez déjà répondu à cette question de sondage.'}, status=400)

    form = ReponseSondageForm(data)
    if form.is_valid():
        response = form.save(commit=False)
        response.question = question
        response.etudiant = request.user
        response.save()
        return JsonResponse({'status': 'success', 'message': 'Réponse de sondage enregistrée avec succès !'})
    else:
        return JsonResponse({'status': 'error', 'errors': form.errors, 'message': "Erreur lors de l'enregistrement de la réponse de sondage."}, status=400)

@activity_owner_or_admin_required
def list_sondage_questions(request, activity_id):
    activite = get_object_or_404(Activite, pk=activity_id, activity_type='SONDAGE')
    questions = activite.questions_sondage.all()
    questions_data = [{'id': q.id, 'intitule': q.intitule} for q in questions]
    return JsonResponse({'questions': questions_data})

@question_owner_or_admin_required
@require_POST
def delete_sondage_question(request, question_id):
    question = get_object_or_404(QuestionSondage, pk=question_id)
    question.delete()
    return JsonResponse({'status': 'success', 'message': 'Question de sondage supprimée avec succès !'})