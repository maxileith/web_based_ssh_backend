# Generated by Django 3.1.7 on 2021-04-23 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saved_sessions', '0003_auto_20210416_0721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sshsession',
            name='port',
            field=models.IntegerField(default=0),
        ),
    ]
