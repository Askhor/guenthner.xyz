from django.db import models
from django.utils import timezone


class GlobalPermission(models.Model):
    # no fields needed; optional descriptive field
    name = models.CharField(max_length=128, blank=True)

    class Meta:
        verbose_name = "Global Permissions"
        verbose_name_plural = "Global Permissions"
        permissions = [
            ("ffs", "FFS")
        ]


class FilePacket(models.Model):
    NEW = "NEW"
    FAILED = "FAILED"
    PENDING = "PENDING"
    STORED = "STORED"

    hsh = models.CharField(max_length=128, blank=True, primary_key=True)
    file = models.CharField(max_length=128, null=True, blank=True, default=None)
    status = models.CharField(choices={s: s for s in [NEW, FAILED, PENDING, STORED]}, max_length=20,
                              default=NEW)
    upload_date = models.DateTimeField(default=timezone.now)
    last_used = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.last_used = timezone.now()
        super().save(*args, **kwargs)
