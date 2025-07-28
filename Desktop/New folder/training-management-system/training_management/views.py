from django.http import HttpResponse
from django.shortcuts import render

def home(request):
    """Home page view"""
    context = {
        'title': 'Training Management System',
        'description': 'Bienvenue sur votre plateforme de gestion de formations'
    }
    return render(request, 'home.html', context)
