from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    # La page principale qui affiche le tableau
    path('utilisateurs/', views.user_management_page, name='user_management'),
    path('cours/', views.course_management_page, name='course_management'),
    path('cours/<int:course_id>/', views.course_detail_page, name='course_detail_page'),
    path('categories/', views.category_management_page, name='category_management_page'),

    # Les "API" pour les actions en arrière-plan
    path('api/users/create/', views.create_user, name='api_create_user'),
    path('api/users/<int:user_id>/', views.user_detail, name='api_user_detail'),
    path('api/users/<int:user_id>/update/', views.update_user, name='api_update_user'),
    path('api/users/<int:user_id>/delete/', views.delete_user, name='api_delete_user'),
    path('api/users/<int:user_id>/lock/', views.lock_user, name='api_lock_user'),
    path('api/users/<int:user_id>/unlock/', views.unlock_user, name='api_unlock_user'),

    # API pour les cours
    path('api/courses/create/', views.create_course, name='api_create_course'),
    path('api/courses/<int:course_id>/', views.course_detail, name='api_course_detail'),
    path('api/courses/<int:course_id>/update/', views.update_course, name='api_update_course'),
    path('api/courses/<int:course_id>/delete/', views.delete_course, name='api_delete_course'),
    path('cours/<int:course_id>/progress/', views.course_progress_view, name='course_progress'),

    # API pour les catégories
    path('api/categories/create/', views.create_category, name='api_create_category'),
    path('api/categories/<int:category_id>/', views.category_detail, name='api_category_detail'),
    path('api/categories/<int:category_id>/update/', views.update_category, name='api_update_category'),
    path('api/categories/<int:category_id>/delete/', views.delete_category, name='api_delete_category'),
    path('reports/', views.reports_page, name='reports_page'),
    path('audit-logs/', views.audit_logs_page, name='audit_logs_page'),
]
