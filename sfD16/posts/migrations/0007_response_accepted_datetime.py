# Generated by Django 5.0.1 on 2024-01-16 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_rename_user_response_sender_response_accepted'),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='accepted_datetime',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
