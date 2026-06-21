from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_payment'),
    ]

    operations = [
        migrations.RenameField(
            model_name='feature',
            old_name='feature',
            new_name='description',
        ),
    ]
