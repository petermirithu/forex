# Generated by Django 2.2 on 2020-01-15 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forex_app', '0003_auto_20200110_0949'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account_price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.IntegerField(default=1000)),
                ('account_type', models.CharField(max_length=50)),
            ],
        ),
    ]
