from django.contrib import admin
from .models import ForumQuestion, ForumComment

admin.site.register(ForumQuestion)
admin.site.register(ForumComment)
