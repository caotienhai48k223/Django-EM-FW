# Generated by Django 5.1 on 2024-09-08 13:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('face_id', '0010_alter_attendance_checked_in'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='checked_in',
        ),
        migrations.RemoveField(
            model_name='attendance',
            name='checked_out',
        ),
    ]
