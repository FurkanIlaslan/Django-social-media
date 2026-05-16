from django.urls import path
from . import views

urlpatterns = [
    path('', views.conversation_list, name='conversation_list'),
    path('<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('<int:conversation_id>/new/', views.get_new_messages, name='get_new_messages'),
    path('start/<str:username>/', views.start_conversation, name='start_conversation'),
]
