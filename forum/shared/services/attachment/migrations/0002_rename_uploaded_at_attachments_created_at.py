# Generated by Django 5.2 on 2025-04-25 12:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attachment', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='attachments',
            old_name='uploaded_at',
            new_name='created_at',
        ),
    ]
