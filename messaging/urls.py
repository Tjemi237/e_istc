from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('new/<int:recipient_id>/', views.new_conversation, name='new_conversation'),
    path('search_users/', views.search_users, name='search_users'),
]