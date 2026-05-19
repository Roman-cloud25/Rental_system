"""
ГЕНЕРАЦИЯ ТЕСТОВЫХ ДАННЫХ
Запуск: python generate_test_data.py
"""

import os
import random
import django
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rental.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction, connection, models
from common.models import City
from properties.models import Property, PropertyType
from bookings.models import Booking
from reviews.models import Review
from analytics.models import SearchHistory, ViewHistory

User = get_user_model()

DEFAULT_PASSWORD = 'testpass123'
PROPERTY_TITLES = ['Cozy', 'Modern', 'Spacious', 'Bright', 'Central',
                   'Quiet', 'Luxury', 'Charming', 'Stylish', 'Sunny']


def random_price():
    return Decimal(random.randint(30, 300))


def random_rooms():
    return Decimal(random.choice([1, 1.5, 2, 2.5, 3, 3.5, 4, 5]))


def random_date_future():
    today = timezone.now().date()
    start = today + timedelta(days=1)
    end = today + timedelta(days=180)
    delta = (end - start).days
    if delta <= 0:
        return today + timedelta(days=7)
    return start + timedelta(days=random.randint(0, delta))


def random_date_past():
    today = timezone.now().date()
    start = today - timedelta(days=180)
    end = today - timedelta(days=1)
    delta = (end - start).days
    if delta <= 0:
        return today - timedelta(days=7)
    return start + timedelta(days=random.randint(0, delta))


def random_date_range_past():
    """Возвращает (start_date, end_date) обе в прошлом, end > start"""
    start = random_date_past()
    today = timezone.now().date()
    max_end = today - timedelta(days=1)
    if start >= max_end:
        start = max_end - timedelta(days=2)
    delta = random.randint(1, 10)
    end = start + timedelta(days=delta)
    if end > max_end:
        end = max_end
    if end <= start:
        end = start + timedelta(days=1)
    return start, end


def create_users():
    print("\n📌 Создание пользователей...")
    users = {'admin': None, 'landlord': None, 'tenant': None, 'both': None, 'extra': []}

    admin, _ = User.objects.get_or_create(
        email='admin@test.com',
        defaults={'name': 'Admin User', 'is_staff': True, 'is_superuser': True,
                  'is_active': True, 'is_tenant': True, 'is_landlord': True, 'role': 'admin'}
    )
    if _:
        admin.set_password('admin123')
        admin.save()
        print("  ✓ Администратор: admin@test.com / admin123")
    users['admin'] = admin

    landlord, _ = User.objects.get_or_create(
        email='landlord@test.com',
        defaults={'name': 'Test Landlord', 'is_active': True,
                  'is_tenant': False, 'is_landlord': True, 'role': 'landlord'}
    )
    if _:
        landlord.set_password('landlord123')
        landlord.save()
        print("  ✓ Арендодатель: landlord@test.com / landlord123")
    users['landlord'] = landlord

    tenant, _ = User.objects.get_or_create(
        email='tenant@test.com',
        defaults={'name': 'Test Tenant', 'is_active': True,
                  'is_tenant': True, 'is_landlord': False, 'role': 'tenant'}
    )
    if _:
        tenant.set_password('tenant123')
        tenant.save()
        print("  ✓ Арендатор: tenant@test.com / tenant123")
    users['tenant'] = tenant

    both, _ = User.objects.get_or_create(
        email='both@test.com',
        defaults={'name': 'Test Both', 'is_active': True,
                  'is_tenant': True, 'is_landlord': True, 'role': 'both'}
    )
    if _:
        both.set_password('both123')
        both.save()
        print("  ✓ Both: both@test.com / both123")
    users['both'] = both

    # Увеличили количество дополнительных пользователей с 3 до 10
    for i in range(1, 11):
        email = f'user{i}@test.com'
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'name': f'Test User {i}', 'is_active': True,
                      'is_tenant': True, 'is_landlord': False, 'role': 'tenant'}
        )
        if created:
            user.set_password(DEFAULT_PASSWORD)
            user.save()
            print(f"  ✓ {email} / {DEFAULT_PASSWORD}")
        users['extra'].append(user)

    return users


def create_properties(users):
    print("\n📌 Создание объявлений...")
    cities = list(City.objects.all())
    property_types = list(PropertyType.objects.all())

    if not cities or not property_types:
        print("  ❌ Нет городов или типов жилья! Запустите 'python manage.py load_initial_data'")
        return []

    landlord = users['landlord']
    both = users['both']
    owners = [landlord, both]
    properties = []
    created_count = 0

    for i in range(30):
        owner = random.choice(owners)
        city = random.choice(cities)
        prop_type = random.choice(property_types)
        title = f"{random.choice(PROPERTY_TITLES)} {prop_type.name} in {city.name}"

        existing = Property.objects.filter(title=title, owner=owner).first()
        if existing:
            properties.append(existing)
            continue

        prop = Property(
            title=title,
            description=f"Beautiful {prop_type.name.lower()} in {city.name}. Near transport, shops.",
            location=city,
            address=f"{random.randint(1,200)} {random.choice(['Berliner Str.', 'Hauptstr.'])}, {city.name}",
            price=random_price(),
            rooms=random_rooms(),
            property_type=prop_type,
            available_from=random_date_future(),
            min_rental_period=random.randint(1, 7),
            owner=owner,
            status=random.choice(['active', 'active', 'active', 'inactive']),
            images=[]
        )
        prop.save()
        properties.append(prop)
        created_count += 1
        print(f"  ✓ {title} (€{prop.price}, {prop.rooms} rooms)")

    print(f"\n  ✅ Создано новых объявлений: {created_count}")
    return properties


def create_bookings(users, properties):
    print("\n📌 Создание бронирований...")
    tenants = [users['tenant'], users['both']] + users['extra']
    bookings = []
    created_count = 0

    # Увеличили долю completed: из 10 статусов 6 completed (60%)
    statuses = [
        'pending', 'confirmed',
        'completed', 'completed', 'completed', 'completed', 'completed', 'completed',
        'cancelled', 'rejected'
    ]

    # Увеличили общее количество попыток бронирований с 20 до 35, чтобы получить больше completed
    for i in range(35):
        tenant = random.choice(tenants)
        available = [p for p in properties if p.status == 'active' and p.owner != tenant]
        if not available:
            continue
        prop = random.choice(available)
        status = random.choice(statuses)

        if status == 'completed':
            start_date, end_date = random_date_range_past()
            nights = (end_date - start_date).days
            total_price = nights * prop.price
            # Вставляем напрямую через SQL, минуя валидацию модели
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO bookings 
                    (listing_id, tenant_id, start_date, end_date, status, total_price, guests, special_requests, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, [
                    prop.id, tenant.id, start_date, end_date, status,
                    total_price, random.randint(1, 4),
                    "Towels please" if random.random() > 0.7 else ""
                ])
            with connection.cursor() as cursor:
                cursor.execute("SELECT LAST_INSERT_ID()")
                booking_id = cursor.fetchone()[0]
            booking = Booking.objects.get(pk=booking_id)
            bookings.append(booking)
            created_count += 1
            print(f"  ✓ Бронирование #{booking.id}: {tenant.email} → {prop.title} ({status})")
        else:
            start_date = random_date_future()
            end_date = start_date + timedelta(days=random.randint(1, 14))
            # Проверка пересечений
            overlapping = Booking.objects.filter(
                listing=prop,
                status__in=['pending', 'confirmed'],
                start_date__lt=end_date,
                end_date__gt=start_date
            )
            if overlapping.exists():
                continue
            nights = (end_date - start_date).days
            total_price = nights * prop.price
            try:
                booking = Booking(
                    listing=prop, tenant=tenant,
                    start_date=start_date, end_date=end_date,
                    status=status, total_price=total_price,
                    guests=random.randint(1, 4),
                    special_requests="Towels please" if random.random() > 0.7 else ""
                )
                booking.save()
                bookings.append(booking)
                created_count += 1
                print(f"  ✓ Бронирование #{booking.id}: {tenant.email} → {prop.title} ({status})")
            except Exception as e:
                print(f"  ✗ Ошибка: {e}")

    # Гарантируем хотя бы одно completed бронирование (если SQL не сработал)
    if not Booking.objects.filter(status='completed').exists():
        print("\n  ⚠️ Нет completed бронирований, создаём принудительно через SQL...")
        tenant = users['tenant']
        prop = next((p for p in properties if p.status == 'active' and p.owner != tenant), None)
        if prop:
            start_date, end_date = random_date_range_past()
            nights = (end_date - start_date).days
            total_price = nights * prop.price
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO bookings 
                    (listing_id, tenant_id, start_date, end_date, status, total_price, guests, special_requests, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, [prop.id, tenant.id, start_date, end_date, 'completed',
                      total_price, 2, "Forced completed booking"])
                cursor.execute("SELECT LAST_INSERT_ID()")
                booking_id = cursor.fetchone()[0]
            booking = Booking.objects.get(pk=booking_id)
            bookings.append(booking)
            created_count += 1
            print(f"  ✓ Принудительно создано completed бронирование #{booking.id}")
        else:
            print("  ❌ Не удалось создать принудительное completed бронирование")

    print(f"\n  ✅ Создано бронирований: {created_count}")
    return bookings


def create_reviews(bookings):
    print("\n📌 Создание отзывов...")
    completed_bookings = [b for b in bookings if b.status == 'completed']

    if not completed_bookings:
        print("  ⚠️ Нет completed бронирований для отзывов")
        return

    for booking in completed_bookings:
        if booking.listing.owner == booking.tenant:
            continue
        if Review.objects.filter(booking=booking).exists():
            continue
        rating = random.randint(3, 5)
        comment = random.choice([
            "Great place, highly recommend!",
            "Very clean and comfortable.",
            "The host was very helpful.",
            "Everything was perfect!",
            "Will definitely book again.",
            "Excellent value for money."
        ])
        Review.objects.create(
            listing=booking.listing,
            user=booking.tenant,
            booking=booking,
            rating=rating,
            comment=comment
        )
        print(f"  ✓ Отзыв: {booking.tenant.email} → {booking.listing.title} (⭐{rating})")

    # Дополнительная гарантия: если отзывов всё ещё нет, создаём принудительно
    if not Review.objects.exists():
        completed = Booking.objects.filter(status='completed').first()
        if completed:
            Review.objects.create(
                listing=completed.listing,
                user=completed.tenant,
                booking=completed,
                rating=5,
                comment="Demo review for presentation"
            )
            print("  ✓ Принудительно создан отзыв")
        else:
            print("  ❌ Нет completed бронирований для отзыва")

    print(f"\n  ✅ Создано отзывов: {Review.objects.count()}")


def create_views(users, properties):
    print("\n📌 Создание истории просмотров...")
    created = 0
    for user in [users['tenant'], users['both']] + users['extra']:
        sample = random.sample(properties, min(5, len(properties)))
        for prop in sample:
            one_day_ago = timezone.now() - timedelta(days=1)
            exists = ViewHistory.objects.filter(user=user, listing=prop, viewed_at__gte=one_day_ago).exists()
            if not exists:
                ViewHistory.objects.create(user=user, listing=prop)
                prop.views_count += 1
                prop.save(update_fields=['views_count'])
                created += 1
    print(f"  ✅ Создано просмотров: {created}")


def create_searches(users):
    print("\n📌 Создание истории поиска...")
    keywords = ['Berlin', 'Munich', 'Hamburg', 'Cologne', 'Frankfurt',
                'apartment', 'house', 'studio', 'luxury', 'cheap']
    created = 0
    for user in [users['tenant'], users['both']] + users['extra']:
        for _ in range(random.randint(2, 5)):
            SearchHistory.objects.create(user=user, keyword=random.choice(keywords))
            created += 1
    print(f"  ✅ Создано поисковых запросов: {created}")


def print_summary():
    from collections import Counter
    print("\n" + "=" * 60)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 60)
    print(f"  👥 Пользователей: {User.objects.count()}")
    print(f"  🏠 Объявлений: {Property.objects.count()}")
    print(f"  📅 Бронирований: {Booking.objects.count()}")
    status_counts = Counter(Booking.objects.values_list('status', flat=True))
    for s, c in status_counts.items():
        print(f"      {s}: {c}")
    print(f"  ⭐ Отзывов: {Review.objects.count()}")
    print("=" * 60)


@transaction.atomic
def generate_all():
    print("\n" + "=" * 60)
    print("🚀 ГЕНЕРАЦИЯ ТЕСТОВЫХ ДАННЫХ")
    print("=" * 60)

    users = create_users()
    properties = create_properties(users)
    if not properties:
        print("❌ Не удалось создать объявления. Проверьте города и типы жилья.")
        return
    bookings = create_bookings(users, properties)
    create_reviews(bookings)
    create_views(users, properties)
    create_searches(users)
    print_summary()
    print("\n✅ Генерация завершена!")
    print("\n🔑 Данные для входа:")
    print("   admin@test.com / admin123")
    print("   landlord@test.com / landlord123")
    print("   tenant@test.com / tenant123")
    print("   both@test.com / both123")
    for i in range(1, 11):
        print(f"   user{i}@test.com / testpass123")
    print("\n💡 JWT токен: POST /api/auth/token/ с email/password")


if __name__ == '__main__':
    generate_all()