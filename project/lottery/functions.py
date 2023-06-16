import random
import string

from django.db import transaction
from django.utils import timezone

from config.models import GlobalConfig
from lottery.constants import WinnerType
from lottery.models import RoundInfo, Ticket, RoundWinners, RoundWinnerDetail
from wallet.constants import WalletType, TransactionType
from wallet.models import Wallet, TransactionLog

WINNER_TYPE_LIST = [item[0] for item in WinnerType.CHOICES]


def generate_ticket_number():
    ticket_number = ''
    for _ in range(6):
        ticket_number += random.choice(string.digits)
    return ticket_number


def check_if_winner(ticket_number, goal):
    if not (len(ticket_number) == len(goal) == 6):
        return None
    counter = 0
    for ticket_item, goal_item in zip(list(ticket_number), list(goal)):
        if ticket_item == goal_item:
            counter += 1
        else:
            break
    return WINNER_TYPE_LIST[counter - 1] if counter else 'lose'


def winner_process_job():
    round_info_qs = RoundInfo.objects.filter(is_done=False)
    if len(round_info_qs) > 1:
        return

    round_info = round_info_qs.last()
    if RoundInfo.objects.filter(number=round_info.number + 1).exists():
        return

    round_detail = RoundWinnerDetail.objects.filter(round=round_info)

    config_qs = GlobalConfig.objects.all()
    ratio_with_type = {config.config_name: config.config_value for config in config_qs}

    with transaction.atomic():
        round_number = round_info.number

        winner_process(round_number)

        round_info.lock_at = timezone.now()
        round_info.is_done = True
        round_info.save()

        total_amount = [detail.total_amount for detail in round_detail if detail.count == 0]
        goal = generate_ticket_number()
        new_round = RoundInfo(number=round_info.number + 1, total_amount=total_amount, goal=goal, previous_round=round_info)
        new_round.save()

        for item in WINNER_TYPE_LIST:
            ratio = ratio_with_type[f'{item}_RATIO']
            RoundWinnerDetail.objects.create(round=new_round, type=item, ratio=ratio)


def winners(round_number):
    round_info = RoundInfo.objects.filter(number=round_number, is_done=False).first()
    if not round_info:
        return None

    goal = round_info.goal
    ticket_qs = Ticket.objects.filter(round=round_info, is_active=True)
    ticket_amount = ticket_qs[0].amount

    result = {item: [] for item in WINNER_TYPE_LIST}

    for ticket in ticket_qs:
        ticket_number = ticket.number
        ticket_winner_type = check_if_winner(ticket_number, goal)
        if not ticket_winner_type and ticket_winner_type == 'lose':
            continue
        result[ticket_winner_type].append(str(ticket.user_id))

    round_winner_detail_qs = RoundWinnerDetail.objects.filter(round__number=round_number)

    with transaction.atomic():
        for winner_type, user_ids in result.items():
            for round_winner_detail in round_winner_detail_qs:
                if round_winner_detail.type == winner_type:
                    round_winner_detail.count = len(user_ids)
                    round_winner_detail.total_amount = ticket_amount * len(user_ids)
                    round_winner_detail.save()

            chunks = [user_ids[i:100 + i] for i in range(0, len(user_ids), 100)]
            for chunk in chunks:
                round_winners = RoundWinners(winner_count=len(chunk), winner_ids=chunk, type=winner_type,
                                             round=round_info)
                round_winners.save()


def winner_process(round_number):
    round_winner_detail_qs = RoundWinnerDetail.objects.filter(round__number=round_number)
    amount_per_user = {detail.type: (detail.total_amount / detail.count) for detail in round_winner_detail_qs}
    round_winner_qs = RoundWinners.objects.filter(is_processed=False, round__number=round_number)
    wallet_qs = Wallet.objects.filter(wallet_type=WalletType.USD)

    for round_winner_obj in round_winner_qs:
        winner_ids = round_winner_obj.winner_ids
        amount = amount_per_user[round_winner_obj.type]

        wallet_qs = wallet_qs.filter(identifier__in=winner_ids).select_for_update()
        with transaction.atomic():
            for wallet_obj in wallet_qs:
                wallet_obj.balance += amount
                wallet_obj.save()

                transaction_log = TransactionLog(wallet=wallet_obj, amount=amount, balance_after=wallet_obj.balance,
                                                 transaction_type=TransactionType.LOTTERY)
                transaction_log.save()

            round_winner_obj.is_processed = True
            round_winner_obj.save()
