import datetime

from django.db import models


class GlobalPermission(models.Model):
    # no fields needed; optional descriptive field
    name = models.CharField(max_length=128, blank=True)

    class Meta:
        verbose_name = "Global Permissions"
        verbose_name_plural = "Global Permissions"
        permissions = [
            ("ffs", "FFS")
        ]


class Setting(models.Model):
    name = models.CharField(max_length=128, blank=True)
    value = models.CharField(max_length=128, blank=True)


class FilePacket(models.Model):
    NEW = "NEW"
    FAILED = "FAILED"
    OUTSTANDING = "OUTSTANDING"
    STORED = "STORED"

    hsh = models.CharField(max_length=128, blank=True, primary_key=True)
    file = models.CharField(max_length=128, null=True, blank=True, default=None)
    status = models.CharField(choices={s: s for s in [NEW, FAILED, OUTSTANDING, STORED]}, max_length=20,
                              default=NEW)
    upload_date = models.DateTimeField(default=datetime.datetime.now)
    pass
