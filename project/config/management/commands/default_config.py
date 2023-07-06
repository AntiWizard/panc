from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction

from config.models import GlobalConfig
from lottery.functions import generate_ticket_number, WINNER_TYPE_LIST
from lottery.models import RoundInfo, RoundDetail
from wallet.constants import WalletType
from wallet.models import Wallet


class Command(BaseCommand):
    help = 'Creates a config before start project'

    def handle(self, *args, **options):
        try:
            default_config = {
                'RATIO_WIN_1': 2,
                'RATIO_WIN_2': 3,
                'RATIO_WIN_3': 5,
                'RATIO_WIN_4': 10,
                'RATIO_WIN_5': 20,
                'RATIO_WIN_6': 40,
                'BURN_RATIO': 20,
                'SWAP_RATIO': 0.5,
                'FAKE_ROUND_PRICE': 0,
                'TICKET_AMOUNT': 50,
                'ADMIN_WALLET': '',
                'ADMIN_PRIVATE_KEY': '',
                'INFURA_API_KEY': settings.INFURA_API_KEY,
                'API_KEY_CRYPTOCOMPARE': settings.API_KEY_CRYPTOCOMPARE
            }
            copy_config = default_config.copy()

            global_config_qs = GlobalConfig.objects.filter(is_active=True).all()
            global_configs = {config.config_name: config.config_value for config in global_config_qs}
            duplicate_list = []
            for key, values in default_config.items():
                if key in global_configs.keys():
                    duplicate_list.append(key)
            [default_config.pop(item) for item in duplicate_list]

            with transaction.atomic():
                GlobalConfig.objects.bulk_create(
                    [GlobalConfig(config_name=name, config_value=values) for name, values in default_config.items()])

                if not Wallet.objects.filter(wallet_type=WalletType.MAIN, flagged_wallet=True).exists():
                    Wallet.objects.create(wallet_type=WalletType.MAIN, flagged_wallet=True)

                if not RoundInfo.objects.exists():
                    round_obj = RoundInfo.objects.create(ticket_goal=generate_ticket_number(),
                                                         ticket_amount=copy_config['TICKET_AMOUNT'])
                    for item in WINNER_TYPE_LIST:
                        ratio = copy_config[f'RATIO_{item.upper()}']
                        RoundDetail.objects.create(round=round_obj, type=item, ratio=ratio)
        except:
            pass
