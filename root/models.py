from django.contrib.auth.models import User
from django.db import models
from django.db.models import SET_NULL


class GlobalPermission(models.Model):
    # no fields needed; optional descriptive field
    name = models.CharField(max_length=128, blank=True)

    class Meta:
        verbose_name = "Global Permissions"
        verbose_name_plural = "Global Permissions"
        permissions = [
            ("admin", "Admin functions"),
        ]


class ChatMessage(models.Model):
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=SET_NULL, null=True)
    time = models.DateTimeField(auto_now_add=True)
