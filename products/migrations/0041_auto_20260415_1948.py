from django.db import migrations

def make_image_alt_nullable(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            cursor.execute('ALTER TABLE products_productimage ALTER COLUMN image_alt DROP NOT NULL;')

def make_image_alt_not_nullable(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            cursor.execute('ALTER TABLE products_productimage ALTER COLUMN image_alt SET NOT NULL;')


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0040_alter_productimage_image_alt'),
    ]

    operations = [
        migrations.RunPython(make_image_alt_nullable, make_image_alt_not_nullable),
    ]
