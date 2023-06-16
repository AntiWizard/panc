from django.contrib.postgres import fields
from django.db import models

from lottery.constants import WinnerType
from user.models import AbstractBaseModelWithUUidAsPk, User


class RoundInfo(models.Model):
    goal = models.CharField(max_length=128, editable=False)  # hash
    burn_amount = models.FloatField(default=0.0)
    total_amount = models.FloatField(default=0.0)
    ticket_count = models.IntegerField(default=0)
    previous_round = models.ForeignKey(to='self', null=True, blank=True, default=None, on_delete=models.CASCADE)
    is_done = models.BooleanField(default=False)

    lock_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


class Ticket(AbstractBaseModelWithUUidAsPk):
    round_number = models.ForeignKey(to=RoundInfo, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.DO_NOTHING)
    amount = models.FloatField()
    number = models.CharField(max_length=6, editable=False)  # validation
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)


class RoundWinners(models.Model):
    winner_count = models.IntegerField(default=0)  # 1 >= x >= 100
    winner_ids = fields.ArrayField(base_field=models.UUIDField(), default=list)
    type = models.CharField(choices=WinnerType.CHOICES, default=WinnerType.CHOICES)
    round = models.ForeignKey(to=RoundInfo, on_delete=models.DO_NOTHING)
    is_processed = models.BooleanField(default=False)
