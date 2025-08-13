from django.urls import path
from . import views

app_name = 'forums'

urlpatterns = [
    path('cours/<int:course_id>/', views.forum_cours, name='forum_cours'),
    path('sujet/<int:sujet_id>/', views.details_sujet, name='details_sujet'),
    path('cours/<int:course_id>/nouveau_sujet/', views.creer_sujet, name='creer_sujet'),
    path('sujet/<int:sujet_id>/repondre/', views.ajouter_message, name='ajouter_message'),
    path('message/<int:message_id>/supprimer/', views.supprimer_message, name='supprimer_message'),
    path('sujet/<int:sujet_id>/supprimer/', views.supprimer_sujet, name='supprimer_sujet'),
]
