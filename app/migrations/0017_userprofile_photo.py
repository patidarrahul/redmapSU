# Generated by Django 5.0.6 on 2024-08-13 14:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_alter_layer_coating_method_spraypyrolysis_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
