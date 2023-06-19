from eth_utils import is_hex_address
from django import forms


def validate_eth_address(value):
    if not is_hex_address(value):
        raise forms.ValidationError(
            '%(value)s is not a valid Ethereum address',
            params={'value': value},
        )
