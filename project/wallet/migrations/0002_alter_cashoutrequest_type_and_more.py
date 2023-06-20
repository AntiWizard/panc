# Generated by Django 4.1.4 on 2023-06-20 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashoutrequest',
            name='type',
            field=models.CharField(choices=[('usd', 'usd'), ('etr', 'etr'), ('btc', 'btc')], default='usd', max_length=5),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='currency_swap',
            field=models.CharField(blank=True, choices=[('usd', 'usd'), ('etr', 'etr'), ('btc', 'btc')], default=None, max_length=5, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='currency_type',
            field=models.CharField(choices=[('usd', 'usd'), ('etr', 'etr'), ('btc', 'btc')], default='usd', max_length=5),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(choices=[('pending', 'pending'), ('failed', 'failed'), ('success', 'success'), ('approved', 'approved')], default='pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='transactionlog',
            name='transaction_type',
            field=models.CharField(choices=[('cashout', 'cashout'), ('transaction', 'transaction'), ('lottery', 'lottery'), ('burn', 'burn')], default='transaction', max_length=15),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='wallet_type',
            field=models.CharField(choices=[('usd', 'usd'), ('main', 'main')], default='usd', max_length=5),
        ),
    ]
