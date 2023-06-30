import requests
from django.conf import settings

from config.models import GlobalConfig
from wallet.constants import CurrencyType

CURRENCY_TYPE_LIST = [item[0] for item in CurrencyType.CHOICES]


def convert_currency_to_usd(src_symbol, des_symbol=CurrencyType.USD):
    if src_symbol.lower() not in CURRENCY_TYPE_LIST:
        return

    data = {}

    cryptocompare_api_key = GlobalConfig.objects.filter(config_name='API_KEY_CRYPTOCOMPARE').first()
    if not cryptocompare_api_key:
        return data

    url = f'{settings.CONVERT_API_CURRENCY_V1}?fsym={src_symbol}&tsyms={des_symbol}'
    url += f'&api_key={cryptocompare_api_key.config_value}'

    try:
        response = requests.get(url=url)
        if response.status_code == 200:
            data = response.json()
        return data
    except:
        return data
