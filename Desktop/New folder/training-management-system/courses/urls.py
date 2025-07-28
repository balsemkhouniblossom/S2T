from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Course list
    path('', views.courses_list, name='list'),
    
    # Course details and learning
    path('<int:course_id>/', views.course_detail, name='detail'),
    path('<int:course_id>/enroll/', views.course_enroll, name='enroll'),
    path('<int:course_id>/watch/', views.course_watch, name='watch'),
    
    # Course management
    path('create/', views.course_create, name='create'),
    
    # My courses
    path('my-courses/', views.my_courses, name='my_courses'),
]
