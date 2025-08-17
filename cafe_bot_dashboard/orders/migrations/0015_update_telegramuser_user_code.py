# Generated manually to fix user_code generation

from django.db import migrations, models
import django.db.models.deletion


def update_user_codes(apps, schema_editor):
    """Update existing user codes to be sequential starting from 10000"""
    TelegramUser = apps.get_model('orders', 'TelegramUser')
    
    # Get all users ordered by creation time (ID)
    users = TelegramUser.objects.order_by('id')
    
    # Start from 10000
    next_code = 10000
    
    for user in users:
        user.user_code = next_code
        user.save()
        next_code += 1


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0014_configreport'),
    ]

    operations = [
        migrations.RunPython(update_user_codes, reverse_code=migrations.RunPython.noop),
    ]
