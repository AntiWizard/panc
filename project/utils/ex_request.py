import requests
from django.conf import settings

from wallet.constants import CurrencyType

CURRENCY_TYPE_LIST = [item[0] for item in CurrencyType.CHOICES]


def convert_currency_to_usdt(symbol):
    if symbol.lower() not in CURRENCY_TYPE_LIST:
        return

    url = settings.CONVERT_API_CURRENCY_V1 + f'?symbol={symbol.upper()}USDT'
    data = {}
    try:
        response = requests.get(url=url, headers={'X-Api-Key': settings.API_KEY})
        if response.status_code == 200:
            data = response.json()
        return data
    except:
        return data
