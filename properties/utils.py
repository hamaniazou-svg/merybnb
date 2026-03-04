"""
Utility functions for calendar synchronization.
"""

import requests
from datetime import datetime
from icalendar import Calendar

from bookings.models import Booking


def fetch_and_parse_ical(url: str) -> list:
    """
    Fetch and parse an iCal feed.
    """
    events = []

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        calendar = Calendar.from_ical(response.content)

        for component in calendar.walk():
            if component.name == "VEVENT":

                uid = str(component.get("UID"))
                dtstart = component.get("DTSTART").dt
                dtend = component.get("DTEND").dt

                if not isinstance(dtstart, datetime):
                    dtstart = datetime.combine(dtstart, datetime.min.time())

                if not isinstance(dtend, datetime):
                    dtend = datetime.combine(dtend, datetime.min.time())

                events.append({
                    "uid": uid,
                    "start_date": dtstart,
                    "end_date": dtend,
                })

    except Exception as e:
        print(f"[iCal Sync Error] {e}")

    return events


def sync_property_calendars(property_obj):
    """
    Sync calendars and SAVE bookings to DB.
    """

    results = []

    sources = [
        ("airbnb", property_obj.airbnb_ical_url),
        ("booking", property_obj.booking_ical_url),
    ]

    for source_name, url in sources:

        if not url:
            continue

        events = fetch_and_parse_ical(url)

        for event in events:

            booking, created = Booking.objects.update_or_create(
                uid=event["uid"],
                defaults={
                    "property": property_obj,
                    "start_date": event["start_date"],
                    "end_date": event["end_date"],
                    "source": source_name,
                }
            )

            results.append({
                "uid": booking.uid,
                "created": created
            })

    return results
