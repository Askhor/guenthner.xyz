from django.contrib import admin

from private.models import Setting


class SettingAdmin(admin.ModelAdmin):
    list_display = ("name", "value")


admin.site.register(Setting, SettingAdmin)
