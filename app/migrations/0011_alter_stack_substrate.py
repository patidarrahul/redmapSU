# Generated by Django 5.0.6 on 2024-07-30 12:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_alter_coatingparameters_infilteration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stack',
            name='substrate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.inventory'),
        ),
    ]
