"""Dev utility — seed sample orders, addresses, zones, deliveries, and drivers."""
import sys
import os
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Zone, DeliveryAddress, Order, OrderItem, Delivery, Driver, User, Role, UserRole
from app.core.security import hash_password


def seed_sample_data(db: Session) -> None:
    if db.query(Order).count() > 0:
        print("Sample data already exists. Skipping.")
        return

    admin = db.query(User).filter(User.email == "admin@logistics.local").first()
    if not admin:
        from app.db_seed import seed
        seed(db)
        admin = db.query(User).filter(User.email == "admin@logistics.local").first()
        if not admin:
            print("ERROR: could not find admin user after seed.")
            return

    zones = [
        Zone(name="Downtown"),
        Zone(name="North District"),
        Zone(name="East Industrial"),
        Zone(name="West Suburbs"),
    ]
    for z in zones:
        db.add(z)
    db.flush()

    addresses_data = [
        ("123 River Rd",    "Downtown",   zones[0].id, 40.7128, -74.0060),
        ("45 Oak Lane",     "Northville", zones[1].id, 40.7300, -74.0100),
        ("78 Hill St",      "Downtown",   zones[0].id, 40.7150, -74.0080),
        ("234 Maple Ave",   "Eastbrook",  zones[2].id, 40.7200, -73.9900),
        ("567 Pine Dr",     "Westwood",   zones[3].id, 40.7050, -74.0300),
        ("890 Cedar Blvd",  "Downtown",   zones[0].id, 40.7110, -74.0070),
        ("321 Elm St",      "Northville", zones[1].id, 40.7320, -74.0120),
        ("654 Birch Way",   "Eastbrook",  zones[2].id, 40.7220, -73.9880),
    ]
    addresses = []
    for line1, city, zone_id, lat, lng in addresses_data:
        addr = DeliveryAddress(
            zone_id=str(zone_id),
            line1=line1,
            city=city,
            country="US",
            lat=lat + random.uniform(-0.005, 0.005),
            lng=lng + random.uniform(-0.005, 0.005),
        )
        db.add(addr)
        addresses.append(addr)
    db.flush()

    driver_role = db.query(Role).filter(Role.code == "DRIVER").first()
    drivers = []
    for i in range(3):
        driver_user = User(
            email=f"driver{i + 1}@logistics.local",
            password_hash=hash_password("driver123"),
            full_name=f"Driver {chr(65 + i)}. Smith",
            is_active=True,
        )
        db.add(driver_user)
        db.flush()
        db.add(UserRole(user_id=driver_user.id, role_id=driver_role.id))
        driver = Driver(
            user_id=str(driver_user.id),
            license_number=f"DL{1000 + i}",
            phone=f"+1-555-010{i}",
            status="AVAILABLE" if i < 2 else "OFF_DUTY",
            auto_assign_eligible=True,
            current_location={"lat": 40.7128 + i * 0.01, "lng": -74.0060 + i * 0.01},
        )
        db.add(driver)
        drivers.append(driver)
    db.flush()

    customers = [
        ("Alice Johnson", "+1-555-0101", "alice@example.com"),
        ("Bob Martinez",  "+1-555-0102", "bob@example.com"),
        ("Carol Davis",   "+1-555-0103", "carol@example.com"),
        ("David Lee",     "+1-555-0104", "david@example.com"),
        ("Emma Wilson",   "+1-555-0105", "emma@example.com"),
        ("Frank Brown",   "+1-555-0106", "frank@example.com"),
        ("Grace Taylor",  "+1-555-0107", "grace@example.com"),
        ("Henry Clark",   "+1-555-0108", "henry@example.com"),
    ]
    # Valid statuses from Order model
    order_statuses = ["DRAFT", "CONFIRMED", "PREPARING", "READY_FOR_PICKUP"]
    # Valid statuses from Delivery model
    delivery_statuses = ["PREPARATION", "IN_TRANSIT", "DELIVERED"]

    now = datetime.utcnow()

    for i, (customer_name, phone, email) in enumerate(customers):
        order = Order(
            external_reference=f"ORD-{2041 + i}",
            delivery_address_id=str(addresses[i].id),
            customer_name=customer_name,
            customer_phone=phone,
            customer_email=email,
            status=order_statuses[i % len(order_statuses)],
            requested_delivery_start=now + timedelta(hours=i),
            requested_delivery_end=now + timedelta(hours=i + 2),
            total_weight_kg=10.0 + (i * 5),
            notes=f"Sample order {i + 1}" if i % 2 == 0 else None,
            created_by=str(admin.id),
        )
        db.add(order)
        db.flush()

        for j in range(random.randint(1, 3)):
            db.add(OrderItem(
                order_id=str(order.id),
                sku=f"SKU-{1000 + i * 10 + j}",
                description=f"Product {chr(65 + j)} for order {i + 1}",
                quantity=random.randint(1, 5),
                weight_kg=round(2.0 + random.uniform(0, 3), 2),
            ))

        if i < 7:
            delivery = Delivery(
                order_id=str(order.id),
                status=delivery_statuses[i % len(delivery_statuses)],
                estimated_distance_km=5.0 + (i * 2),
                estimated_duration_mins=20 + (i * 5),
                estimated_arrival=now + timedelta(hours=i + 1),
            )
            if i < 5:
                delivery.driver_id = str(drivers[i % len(drivers)].id)
                delivery.assigned_by = str(admin.id)
                delivery.assigned_at = now - timedelta(minutes=30)
            db.add(delivery)

    db.commit()
    print("✅ Sample data seeded:")
    print(f"   {len(zones)} zones, {len(addresses)} addresses, {len(drivers)} drivers")
    print(f"   {len(customers)} orders, 7 deliveries (5 assigned)")
    print("\nCredentials:")
    print("   admin@logistics.local / admin123")
    print("   driver1@logistics.local / driver123")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_sample_data(db)
    finally:
        db.close()
