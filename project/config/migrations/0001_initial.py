# Generated by Django 4.2.2 on 2023-06-19 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('config_name', models.CharField(max_length=200, unique=True)),
                ('config_value', models.CharField(max_length=300)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]
