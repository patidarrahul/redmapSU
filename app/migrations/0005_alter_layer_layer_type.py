# Generated by Django 5.0.6 on 2024-06-20 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_layercomposition_options_layer_layer_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='layer',
            name='layer_type',
            field=models.CharField(choices=[('Coating Layer', 'Coated Layer'), ('Surface Treatment', 'Surface Treatment')], default='Coated Layer', max_length=100),
        ),
    ]
