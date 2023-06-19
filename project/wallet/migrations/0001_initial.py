# Generated by Django 4.2.2 on 2023-06-19 09:34

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Wallet',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('identifier', models.CharField(max_length=42)),
                ('wallet_type', models.CharField(choices=[('usd', 'usd'), ('main', 'main')], default='usd')),
                ('balance', models.DecimalField(decimal_places=5, default=0.0, max_digits=20)),
                ('flagged_wallet', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='TransactionLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=5, max_digits=20)),
                ('temp_transaction_ref', models.CharField(blank=True, default=None, max_length=36, null=True)),
                ('transaction_type', models.CharField(choices=[('cashout', 'cashout'), ('transaction', 'transaction'), ('lottery', 'lottery'), ('burn', 'burn')], default='transaction')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='wallet.wallet')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=5, max_digits=20)),
                ('currency_type', models.CharField(choices=[('usd', 'usd'), ('etr', 'etr'), ('btc', 'btc')], default='usd')),
                ('currency_swap', models.CharField(blank=True, choices=[('usd', 'usd'), ('etr', 'etr'), ('btc', 'btc')], default='usd', null=True)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('failed', 'failed'), ('success', 'success'), ('approved', 'approved')], default=(('pending', 'pending'), ('failed', 'failed'), ('success', 'success'), ('approved', 'approved')))),
                ('is_swap', models.BooleanField(default=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='wallet.wallet')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CashOutRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('usd', 'usd'), ('etr', 'etr'), ('btc', 'btc')], default='usd')),
                ('amount', models.DecimalField(decimal_places=3, max_digits=10)),
                ('is_canceled', models.BooleanField(default=False)),
                ('is_reserved', models.BooleanField(default=False)),
                ('is_processed', models.BooleanField(default=False)),
                ('description', models.CharField(blank=True, default=None, max_length=500, null=True)),
                ('canceled_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('reserved_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('processed_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='user.user')),
            ],
        ),
    ]
