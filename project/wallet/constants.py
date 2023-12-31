class WalletType:
    USD = 'usd'
    MAIN = 'main'

    CHOICES = (
        (USD, 'usd'),
        (MAIN, 'main'),
    )


class CurrencyType:
    USD = 'usd'
    ETH = 'eth'
    BTC = 'btc'

    CHOICES = (
        (USD, 'usd'),
        (ETH, 'eth'),
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
