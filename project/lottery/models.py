from django.contrib.postgres import fields
from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.db import models

from lottery.constants import WinnerType
from user.models import AbstractBaseModelWithUUidAsPk, User


class RoundInfo(models.Model):
    number = models.IntegerField(default=1, unique=True)
    goal = models.CharField(max_length=128, editable=False)  # hash
    total_amount = models.FloatField(default=0.0)
    burn_amount = models.FloatField(default=0.0)
    ticket_count = models.IntegerField(default=0)
    previous_round = models.ForeignKey(to='self', null=True, blank=True, default=None, on_delete=models.CASCADE)
    is_done = models.BooleanField(default=False)

    lock_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.number


class Ticket(AbstractBaseModelWithUUidAsPk):
    round = models.ForeignKey(to=RoundInfo, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.DO_NOTHING)
    amount = models.FloatField()
    number = models.CharField(max_length=6, editable=False,
                              validators=[MaxLengthValidator(6), MinLengthValidator(6)])
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.id + " > " + self.round.number


class RoundWinnerDetail(models.Model):
    count = models.IntegerField()
    type = models.CharField(choices=WinnerType.CHOICES, default=WinnerType.CHOICES)
    round = models.ForeignKey(to=RoundInfo, on_delete=models.CASCADE)
    total_amount = models.FloatField()
    ratio = models.FloatField()

    def __str__(self):
        return self.round.number


class RoundWinners(models.Model):
    winner_count = models.IntegerField(default=0)  # 1 >= x >= 100
    winner_ids = fields.ArrayField(base_field=models.UUIDField(), default=list)
    type = models.CharField(choices=WinnerType.CHOICES, default=WinnerType.CHOICES)
    round = models.ForeignKey(to=RoundInfo, on_delete=models.DO_NOTHING)
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return self.round.number
