# Generated by Django 5.1 on 2024-09-08 05:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('face_id', '0003_delete_log'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='bio',
        ),
        migrations.AddField(
            model_name='profile',
            name='dob',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
