import requests
from django.conf import settings

from wallet.constants import CurrencyType

CURRENCY_TYPE_LIST = [item[0] for item in CurrencyType.CHOICES]


def convert_currency_to_usd(src_symbol, des_symbol=CurrencyType.USD):
    if src_symbol.lower() not in CURRENCY_TYPE_LIST:
        return

    url = 'https://min-api.cryptocompare.com/data/price' + f'?fsym={src_symbol}&tsyms={des_symbol}'
    url += f'&api_key={settings.API_KEY_CRYPTOCOMPARE}'
    data = {}
    try:
        response = requests.get(url=url)
        if response.status_code == 200:
            data = response.json()
        return data
    except:
        return data
