# Generated by Django 5.0.6 on 2024-08-28 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_rename_infilteration_coatingparameters_infiltration_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='color',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
