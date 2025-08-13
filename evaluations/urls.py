from django.urls import path
from . import views

app_name = 'evaluations'

urlpatterns = [
    path('api/courses/<int:course_id>/activities/create/', views.create_activity, name='api_create_activity'),
    path('api/activities/<int:activity_id>/', views.activity_detail, name='api_activity_detail'),
    path('api/activities/<int:activity_id>/update/', views.update_activity, name='api_update_activity'),
    path('api/activities/<int:activity_id>/delete/', views.delete_activity, name='api_delete_activity'),

    # API pour les questions et les choix
    path('api/activities/<int:quiz_id>/questions/', views.list_questions, name='api_list_questions'),
    path('api/activities/<int:quiz_id>/questions/create/', views.create_question, name='api_create_question'),
    path('api/questions/<int:question_id>/', views.question_detail, name='api_question_detail'),
    path('api/questions/<int:question_id>/update/', views.update_question, name='api_update_question'),
    path('api/questions/<int:question_id>/delete/', views.delete_question, name='api_delete_question'),

    # API pour la notation des devoirs
    path('api/activities/<int:activity_id>/submissions/', views.list_submissions, name='api_list_submissions'),
    path('api/submissions/<int:submission_id>/grade/', views.grade_submission, name='api_grade_submission'),
    path('sondage/<int:activity_id>/results/', views.sondage_results, name='sondage_results'),
    path('api/sondages/<int:activity_id>/questions/create/', views.create_sondage_question, name='api_create_sondage_question'),
    path('api/sondages/questions/<int:question_id>/submit_response/', views.submit_sondage_response, name='api_submit_sondage_response'),
    path('api/sondages/<int:activity_id>/questions/', views.list_sondage_questions, name='api_list_sondage_questions'),
    path('api/sondages/questions/<int:question_id>/delete/', views.delete_sondage_question, name='api_delete_sondage_question'),
]
