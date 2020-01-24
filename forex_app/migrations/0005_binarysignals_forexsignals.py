# Generated by Django 2.2 on 2020-01-16 07:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forex_app', '0004_account_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForexSignals',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency_pair', models.CharField(max_length=700)),
                ('entry_price', models.IntegerField()),
                ('take_profit', models.IntegerField()),
                ('stop_loss', models.IntegerField()),
                ('signal', models.CharField(max_length=900)),
                ('posted_on', models.DateTimeField(auto_now_add=True)),
                ('posted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BinarySignals',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency_pair', models.CharField(max_length=700)),
                ('chart_time_frame', models.DateTimeField(auto_now_add=True)),
                ('expiration_time', models.DateTimeField()),
                ('signal', models.CharField(max_length=900)),
                ('posted_on', models.DateTimeField(auto_now_add=True)),
                ('posted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]