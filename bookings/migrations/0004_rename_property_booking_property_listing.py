# Generated manually to rename 'property' field to 'property_listing'

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0003_alter_booking_options_remove_booking_end_date_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='booking',
            old_name='property',
            new_name='property_listing',
        ),
    ]
