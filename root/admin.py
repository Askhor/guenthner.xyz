from django.contrib import admin

from root.models import ChatMessage


class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("message", "user", "time")


# Register your models here.
admin.site.register(ChatMessage, ChatMessageAdmin)
