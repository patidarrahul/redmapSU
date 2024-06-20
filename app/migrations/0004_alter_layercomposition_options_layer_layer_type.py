# Generated by Django 5.0.6 on 2024-06-20 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_layercomposition_layer_layer_composition'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='layercomposition',
            options={'verbose_name_plural': 'Layer Composition'},
        ),
        migrations.AddField(
            model_name='layer',
            name='layer_type',
            field=models.CharField(choices=[('Coated Layer', 'Coated Layer'), ('Surface Treatment', 'Surface Treatment')], default='Coated Layer', max_length=100),
        ),
    ]