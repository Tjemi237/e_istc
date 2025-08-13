from django.db import models

class PlatformSettings(models.Model):
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#0D47A1')
    secondary_color = models.CharField(max_length=7, default='#FF9800')

    def __str__(self):
        return "Platform Settings"

    class Meta:
        verbose_name_plural = "Platform Settings"