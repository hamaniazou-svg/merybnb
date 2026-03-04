# 🚀 Quick Start Guide - Merybnb

## ⚡ Get Running in 30 Seconds

```bash
cd C:\Users\PC\rbnbproject
python manage.py runserver
```

Then visit:
- **Admin Panel**: http://localhost:8000/admin  
  - Username: `admin`
  - Password: (reset with `python manage.py changepassword admin`)

- **API**: http://localhost:8000/api/properties/  

- **Detail Page**: http://localhost:8000/properties/{id}/book/

---

## 📝 Create Test Data

### Via Admin Panel
1. Go to http://localhost:8000/admin
2. **Properties** → **Add Property**
3. Fill in details:
   - Name: "Luxury Beach Villa"
   - City: "Meknes"
   - Price per night: 150.00
   - Beds: 3
   - Baths: 2
   - Amenities: Check WiFi, Pool, AC
4. **Save**

### Via Django Shell
```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from properties.models import Property, PropertyImage
from bookings.models import Booking
from datetime import date

# Create user
user = User.objects.create_user('landlord1', 'landlord@example.com', 'password123')

# Create property
prop = Property.objects.create(
    name="Luxury Beach Villa",
    description="Beautiful beachside property",
    owner=user,
    city="Meknes",
    address="123 Beach Street",
    price_per_night=150.00,
    beds=3,
    baths=2,
    has_wifi=True,
    has_pool=True,
    has_ac=True
)

# Add property images
PropertyImage.objects.create(
    property=prop,
    image="property_images/beach1.jpg",
    alt_text="Front view",
    is_primary=True,
    order=0
)

# Create booking
booking = Booking.objects.create(
    property_listing=prop,
    user=user,
    check_in=date(2026, 3, 15),
    check_out=date(2026, 3, 20),
    status='confirmed'
)

print(f"Property: {prop}")
print(f"Total price: ${booking.total_price}")
print(f"Nights: {booking.num_nights}")

exit()
```

---

## 🔌 API Endpoints

### List Properties (Public)
```bash
curl http://localhost:8000/api/properties/
```

### Get Property Detail (Public)
```bash
curl http://localhost:8000/api/properties/1/
```

### Create Property (Authenticated)
```bash
curl -X POST http://localhost:8000/api/properties/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Property",
    "price_per_night": 100,
    "city": "Meknes",
    "beds": 2,
    "baths": 1
  }'
```

### List Bookings (Authenticated)
```bash
curl http://localhost:8000/api/bookings/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Calculate Booking Cost
```bash
curl -X POST http://localhost:8000/api/bookings/calculate-cost/ \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": 1,
    "check_in": "2026-03-15",
    "check_out": "2026-03-20"
  }'
```

Response:
```json
{
  "num_nights": 5,
  "nightly_rate": "150.00",
  "total_price": "750.00",
  "is_available": true
}
```

---

## 🔐 Get JWT Token for API Testing

### 1. Create User
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user('testuser', 'test@example.com', 'pass123')
>>> exit()
```

### 2. Get Token
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "pass123"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. Use Token
```bash
curl http://localhost:8000/api/bookings/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## 🖼️ Upload Images

### Via Admin
1. Create property
2. Scroll to "Property Images" section
3. Click "Add another Property Image"
4. Upload image (auto-resized with Pillow)
5. Set as primary if needed
6. Drag to reorder

### Via Shell
```python
from properties.models import PropertyImage
from django.core.files.images import ImageFile

prop = Property.objects.get(id=1)
image = PropertyImage(
    property=prop,
    alt_text="Living room view",
    order=1
)
image.image.save(
    'living_room.jpg',
    ImageFile(open('path/to/image.jpg', 'rb'))
)
```

---

## 🧪 Common Test Scenarios

### Test 1: Overlapping Bookings
```python
from properties.models import Property
from bookings.models import Booking
from datetime import date

prop = Property.objects.first()

# Create first booking
b1 = Booking(
    property_listing=prop,
    check_in=date(2026, 3, 15),
    check_out=date(2026, 3, 20),
    status='confirmed'
)
b1.save()

# Try to create overlapping booking (should fail validation)
b2 = Booking(
    property_listing=prop,
    check_in=date(2026, 3, 18),  # Overlaps with b1
    check_out=date(2026, 3, 22),
    status='pending'
)

print(b2.is_overlapping)  # True
b2.full_clean()  # Raises ValidationError
```

### Test 2: Auto Price Calculation
```python
from datetime import date

booking = Booking.objects.first()
booking.check_in = date(2026, 3, 15)
booking.check_out = date(2026, 3, 20)

print(f"Nightly rate: ${booking.property_listing.price_per_night}")
print(f"Nights: {booking.num_nights}")
print(f"Total: ${booking.total_price}")

# Output:
# Nightly rate: $150.00
# Nights: 5
# Total: $750.00
```

### Test 3: Multi-tenancy (Owner-Only Edits)
```python
from django.contrib.auth.models import User
from properties.models import Property

# User 1 creates property
user1 = User.objects.get(username='landlord1')
prop = Property.objects.create(
    name="User1's Property",
    owner=user1,
    price_per_night=100
)

# User 2 tries to edit (should fail in API due to permission)
user2 = User.objects.get(username='landlord2')
# In API view: only user1 can PUT/PATCH/DELETE
```

---

## 🔄 Database Management

### Reset Database (SQLite)
```bash
# Delete all data and recreate tables
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Backup Database
```bash
# Linux/Mac
cp db.sqlite3 db.sqlite3.backup

# Windows
copy db.sqlite3 db.sqlite3.backup
```

### Export Data
```bash
python manage.py dumpdata > data.json
python manage.py dumpdata properties > properties.json
python manage.py dumpdata bookings > bookings.json
```

### Import Data
```bash
python manage.py loaddata data.json
```

---

## 🐛 Debugging

### Enable SQL Query Logging
In `settings.py`, add to end:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Check Migrations Status
```bash
python manage.py showmigrations
python manage.py showmigrations --list

# Example output:
# [X] properties.0001_initial
# [X] properties.0002_alter_property_options_property_address_and_more
# [X] properties.0003_property_baths_property_beds_property_has_ac_and_more
# [ ] properties.0004_not_yet_applied
```

### Unapply Migration (Dangerous!)
```bash
python manage.py migrate properties 0002  # Go back to 0002
python manage.py migrate bookings zero    # Remove all bookings migrations
```

---

## 📋 Admin Customization

The admin interface is pre-configured with:
- ✅ Property list with owner, city, price filters
- ✅ PropertyImage inline gallery editor
- ✅ Booking list with status, source, date filters
- ✅ Search by property name, guest name, UID

Visit: http://localhost:8000/admin/properties/property/

---

## 🚨 Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Tenant or user not found` | Bad PostgreSQL creds | Update .env with correct Supabase credentials |
| `Table already exists` | Migration ran twice | Safe, migrations are idempotent |
| `No migrations to apply` | Already up-to-date | Normal, nothing to do |
| `ImproperlyConfigured` | Missing env var | Check .env file exists and is loaded |
| `permission denied` | File permissions issue | On Windows, usually not a problem; on Linux use `chmod` |

---

## ✅ Verification Checklist

- [ ] Database file exists: `ls db.sqlite3`
- [ ] Admin accessible: http://localhost:8000/admin (admin/admin)
- [ ] API accessible: http://localhost:8000/api/properties/
- [ ] Can create property via admin
- [ ] Can create booking via admin
- [ ] Price calculation works (total_price @property)
- [ ] Overlap detection works (is_overlapping @property)

---

**All set!** 🎉  
Start developing and let me know if you hit any issues.
