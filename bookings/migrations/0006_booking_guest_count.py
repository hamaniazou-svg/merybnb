# Generated migration for guest_count field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0005_alter_booking_options_booking_guest_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='guest_count',
            field=models.PositiveIntegerField(blank=True, default=1, help_text='Number of guests for this booking', null=True),
        ),
    ]
