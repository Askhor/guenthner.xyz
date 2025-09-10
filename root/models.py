from django.db import models


class GlobalPermission(models.Model):
    # no fields needed; optional descriptive field
    name = models.CharField(max_length=128, blank=True)

    class Meta:
        verbose_name = "Global Permissions"
        verbose_name_plural = "Global Permissions"
        permissions = [
            ("admin", "Admin functions"),
            ("ffs", "FFS")
        ]
