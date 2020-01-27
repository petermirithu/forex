# Generated by Django 2.2 on 2020-01-27 13:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forex_app', '0006_auto_20200125_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='binarysignals',
            name='signal',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='forexsignals',
            name='signal',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='Blogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blog', models.CharField(max_length=1000)),
                ('posted_on', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=300)),
                ('blog_pic', models.ImageField(blank=True, upload_to='image/')),
                ('posted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
