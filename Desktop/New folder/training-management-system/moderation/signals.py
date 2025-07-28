"""
Signal handlers for automatic content moderation
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from courses.models import CommentaireCours
from messaging.models import MessageGroupe, Message, ReponseDiscussion
from formations.models import Task
from .services import moderate_content_on_save


# Course comments moderation
@receiver(post_save, sender=CommentaireCours)
def moderate_course_comment(sender, instance, created, **kwargs):
    """Automatically moderate course comments"""
    moderate_content_on_save(sender, instance, created, **kwargs)


# Discussion replies moderation
@receiver(post_save, sender=ReponseDiscussion)
def moderate_discussion_reply(sender, instance, created, **kwargs):
    """Automatically moderate discussion replies"""
    moderate_content_on_save(sender, instance, created, **kwargs)


# Group messages moderation
@receiver(post_save, sender=MessageGroupe)
def moderate_group_message(sender, instance, created, **kwargs):
    """Automatically moderate group messages"""
    moderate_content_on_save(sender, instance, created, **kwargs)


# Private messages moderation
@receiver(post_save, sender=Message)
def moderate_private_message(sender, instance, created, **kwargs):
    """Automatically moderate private messages"""
    moderate_content_on_save(sender, instance, created, **kwargs)


# Task descriptions moderation
@receiver(post_save, sender=Task)
def moderate_task_description(sender, instance, created, **kwargs):
    """Automatically moderate task descriptions"""
    moderate_content_on_save(sender, instance, created, **kwargs)
