from django.contrib import admin

from private.models import Setting, FilePacket


class SettingAdmin(admin.ModelAdmin):
    list_display = ("name", "value")


class FilePacketAdmin(admin.ModelAdmin):
    list_display = ("hsh", "file", "status", "upload_date")


admin.site.register(Setting, SettingAdmin)
admin.site.register(FilePacket, FilePacketAdmin)
