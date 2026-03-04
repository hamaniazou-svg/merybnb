from django.core.management.base import BaseCommand
from properties.models import Property
from properties.utils import sync_property_calendars


class Command(BaseCommand):

    help = "Sync bookings for a property"

    def add_arguments(self, parser):
        parser.add_argument("--property_id", type=int)

    def handle(self, *args, **options):

        property_id = options.get("property_id")

        property_obj = Property.objects.get(id=property_id)

        results = sync_property_calendars(property_obj)

        self.stdout.write(f"Processed {len(results)} bookings")
