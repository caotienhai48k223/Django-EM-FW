# Generated by Django 5.1 on 2024-09-07 07:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('face_id', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='face_id.profile'),
        ),
    ]
