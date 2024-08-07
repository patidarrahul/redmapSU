# migrations/0014_copy_fk_to_m2m.py
from django.db import migrations


def copy_fk_to_m2m(apps, schema_editor):
    Layer = apps.get_model('app', 'Layer')
    for layer in Layer.objects.all():
        layer.stacks.add(layer.stack)


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_layer_stacks'),
    ]

    operations = [
        migrations.RunPython(copy_fk_to_m2m),
    ]
