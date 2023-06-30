from django.core.management.base import BaseCommand
from django.conf import settings

from config.models import GlobalConfig


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
                'ADMIN_WALLET': '',
                'INFURA_API_KEY': settings.INFURA_API_KEY,
                'API_KEY_CRYPTOCOMPARE': settings.API_KEY_CRYPTOCOMPARE
            }

            global_config_qs = GlobalConfig.objects.filter(is_active=True).all()
            global_configs = {config.config_name: config.config_value for config in global_config_qs}
            duplicate_list = []
            for key, values in default_config.items():
                if key in global_configs.keys():
                    duplicate_list.append(key)
            [default_config.pop(item) for item in duplicate_list]

            if not default_config:
                return
            GlobalConfig.objects.bulk_create(
                [GlobalConfig(config_name=name, config_value=values) for name, values in default_config.items()])
        except:
            pass
