from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.forum_list, name='list'),
    path('question/<int:question_id>/', views.forum_detail, name='detail'),
    path('post/', views.forum_post_question, name='post_question'),
    path('question/<int:question_id>/comment/', views.forum_post_comment, name='post_comment'),
]
