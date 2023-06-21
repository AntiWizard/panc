import random
import string

from django.db import transaction
from django.db.models import F

from config.models import GlobalConfig
from lottery.constants import WinnerType
from lottery.models import RoundInfo, Ticket, RoundWinners, RoundDetail
from wallet.constants import WalletType, TransactionType
from wallet.models import Wallet, TransactionLog

WINNER_TYPE_LIST = [item[0] for item in WinnerType.CHOICES]


def generate_ticket_number():
    ticket_number = ''
    for _ in range(6):
        ticket_number += random.choice(string.digits)
    return ticket_number


def check_if_winner(ticket_number, ticket_goal):
    if not (len(ticket_number) == len(ticket_goal) == 6):
        return None
    counter = 0
    for ticket_item, goal_item in zip(list(ticket_number), list(ticket_goal)):
        if ticket_item == goal_item:
            counter += 1
        else:
            break
    return WINNER_TYPE_LIST[counter - 1] if counter else 'lose'


def lottery_process():  # job -> 4h
    round_info_qs = RoundInfo.objects.filter(is_done=False)
    if len(round_info_qs) != 1:
        return

    round_info = round_info_qs.first()
    ticket_count = Ticket.objects.filter(is_active=True, round=round_info).count()

    config_qs = GlobalConfig.objects.all()
    config_dict = {config.config_name: config.config_value for config in config_qs}

    burn_ratio = config_dict['BURN_RATIO']

    total_price = round_info.total_price + ticket_count * round_info.ticket_amount
    burn_amount = total_price * burn_ratio / 100

    main_wallet_obj = Wallet.objects.filter(WalletType.MAIN).select_for_update()
    with transaction.atomic():
        # calculate winners
        winners(round_info, winner_total_price=total_price - burn_amount)

        round_info.ticket_count = ticket_count
        round_info.total_price = total_price
        round_info.burn_amount = burn_amount
        round_info.is_done = True
        round_info.save()

        main_wallet_obj.update(balance=F('balance') + burn_amount)
        TransactionLog.objects.create(wallet=main_wallet_obj.first(), amount=+burn_amount,
                                      transaction_type=TransactionType.BURN)

        # next round info
        round_detail = RoundDetail.objects.filter(round=round_info)

        total_amount_miss = sum([detail.total_amount for detail in round_detail if detail.count == 0])

        ticket_goal = generate_ticket_number()
        new_round = RoundInfo(number=round_info.number + 1, ticket_goal=ticket_goal, total_price=total_amount_miss,
                              previous_round=round_info, ticket_amount=config_dict['TICKET_AMOUNT'])
        new_round.save()

        for item in WINNER_TYPE_LIST:
            ratio = config_dict[f'RATIO_{item.upper()}']
            RoundDetail.objects.create(round=new_round, type=item, ratio=ratio)


def winners(round_info, winner_total_price):
    ticket_goal = round_info.ticket_goal

    ticket_qs = Ticket.objects.filter(round=round_info, is_active=True)

    map_type_to_user_ids = {item: [] for item in WINNER_TYPE_LIST}

    for ticket in ticket_qs:
        ticket_number = ticket.number
        ticket_winner_type = check_if_winner(ticket_number, ticket_goal)
        if not ticket_winner_type and ticket_winner_type == 'lose':
            continue
        map_type_to_user_ids[ticket_winner_type].append(str(ticket.user_id))

    round_winner_detail_qs = RoundDetail.objects.filter(round=round_info)

    with transaction.atomic():
        for winner_type, user_ids in map_type_to_user_ids.items():
            for round_winner_detail in round_winner_detail_qs:
                if round_winner_detail.type == winner_type:
                    round_winner_detail.count = len(user_ids)
                    round_winner_detail.total_amount = winner_total_price * round_winner_detail.ratio / 100
                    round_winner_detail.save()

                    break

            chunks = [user_ids[i:100 + i] for i in range(0, len(user_ids), 100)]
            for chunk in chunks:
                round_winners = RoundWinners(winner_count=len(chunk), winner_ids=chunk, type=winner_type,
                                             round=round_info)
                round_winners.save()


def check_if_not_winner_processed():  # job -> 2h
    round_winner_qs = RoundWinners.objects.filter(round__is_done=True, is_processed=False).select_related('round')
    if not round_winner_qs:
        return

    for round_obj in round_winner_qs:
        with transaction.atomic():
            winner_process(round_obj.round.number, round_obj.round.total_price)


def winner_process(round_number, total_price):
    round_detail_qs = RoundDetail.objects.filter(round__number=round_number).select_related('round')
    round_winner_qs = RoundWinners.objects.filter(is_processed=False, round__number=round_number)
    wallet_qs = Wallet.objects.filter(wallet_type=WalletType.USD)

    map_type_to_amount_per_user = {detail.type: ((total_price * detail.ratio) / (detail.count * 100)) for detail in
                                   round_detail_qs}
    for round_winners in round_winner_qs:
        winner_ids = round_winners.winner_ids
        amount = map_type_to_amount_per_user[round_winners.type]

        wallet_qs = wallet_qs.filter(identifier__in=winner_ids).select_for_update()
        with transaction.atomic():
            wallet_qs.update(balance=F('balance') + amount)

            transaction_logs = [TransactionLog(wallet=wallet_obj, amount=+amount, transaction_type=TransactionType.LOTTERY)
                                for wallet_obj in wallet_qs]

            TransactionLog.objects.bulk_create(transaction_logs)

            round_winners.is_processed = True
            round_winners.save()
