import uuid

from django.db import models
from django.utils import timezone

from user.utils import validate_eth_address


class AbstractBaseModelWithUUidAsPk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class User(AbstractBaseModelWithUUidAsPk):
    wallet_address = models.CharField(max_length=42, unique=True, editable=False, validators=[validate_eth_address])

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.id


class UserSession(models.Model):
    session_id = models.CharField(max_length=10, null=False, blank=False, unique=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    # lang = models.CharField(choices=LangChoice.CHOICES, max_length=2, default=LangChoice.EN)

    last_login = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.id
