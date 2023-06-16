from django.db import models


class GlobalConfig(models.Model):
    config_name = models.CharField(max_length=200, unique=True)
    config_value = models.CharField(max_length=300)
    is_active = models.BooleanField(default=True)
