from django.contrib import admin

from private.models import FilePacket, PermissionsRule


class FilePacketAdmin(admin.ModelAdmin):
    list_display = ("hsh", "file", "status", "upload_date", "last_used")


class PermissionsRuleAdmin(admin.ModelAdmin):
    list_display = ("rule", "users", "is_template")


admin.site.register(FilePacket, FilePacketAdmin)
admin.site.register(PermissionsRule, PermissionsRuleAdmin)