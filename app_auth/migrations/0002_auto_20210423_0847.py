# Generated by Django 3.1.7 on 2021-04-23 08:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app_auth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='token',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
