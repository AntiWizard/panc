class WalletType:
    USD = 'usd'
    MAIN = 'main'

    CHOICES = (
        (USD, 'usd'),
        (MAIN, 'main'),
    )


class CurrencyType:
    USD = 'usd'
    ETR = 'etr'
    BTC = 'btc'

    CHOICES = (
        (USD, 'usd'),
        (ETR, 'etr'),
        (BTC, 'btc'),
    )


class TransactionStatus:
    PENDING = 'pending'
    FAILED = 'failed'
    SUCCESS = 'success'
    APPROVED = 'approved'

    CHOICES = (
        (PENDING, 'pending'),
        (FAILED, 'failed'),
        (SUCCESS, 'success'),
        (APPROVED, 'approved'),
    )


class TransactionType:
    CASHOUT = 'cashout'
    TRANSACTION = 'transaction'
    LOTTERY = 'lottery'
    BURN = 'burn'

    CHOICES = (
        (CASHOUT, 'cashout'),
        (TRANSACTION, 'transaction'),
        (LOTTERY, 'lottery'),
        (BURN, 'burn')
    )
