from django.urls import path
from . import views
from .views import create_group

app_name = 'messaging'

urlpatterns = [
    path('inbox/', views.messages_inbox, name='inbox'),
    path('chat/<int:user_id>/', views.chat_conversation, name='chat_conversation'),
    path('message/<int:message_id>/', views.message_detail, name='message_detail'),
    path('compose/', views.message_compose, name='compose'),
    path('groups/', views.groups_list, name='groups'),
    path('groups/create/', create_group, name='create_group'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('discussions/', views.discussions_list, name='discussions'),
    path('discussion/<int:discussion_id>/', views.discussion_detail, name='discussion_detail'),
]
