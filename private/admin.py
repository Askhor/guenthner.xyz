from django.contrib import admin

from private.models import FilePacket


class FilePacketAdmin(admin.ModelAdmin):
    list_display = ("hsh", "file", "status", "upload_date", "last_used")

admin.site.register(FilePacket, FilePacketAdmin)
