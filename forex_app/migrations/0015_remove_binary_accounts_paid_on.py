# Generated by Django 2.2 on 2020-02-04 14:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forex_app', '0014_auto_20200204_1658'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='binary_accounts',
            name='paid_on',
        ),
    ]