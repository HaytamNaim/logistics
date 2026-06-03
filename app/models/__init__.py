"""SQLAlchemy models — match TECHNICAL_BLUEPRINT ER diagram."""
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import (
    Column, String, Boolean, DateTime, ForeignKey, Text, Integer,
    UniqueConstraint, Numeric, JSON, Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship
from app.database import Base


def gen_uuid():
    return str(uuid4())


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    user_roles = relationship("UserRole", back_populates="user")
    driver = relationship("Driver", back_populates="user", uselist=False)


class Role(Base):
    __tablename__ = "roles"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    code = Column(String(64), unique=True, nullable=False)
    name = Column(String(128))
    user_roles = relationship("UserRole", back_populates="role")


class UserRole(Base):
    __tablename__ = "user_roles"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    role_id = Column(UUID(as_uuid=False), ForeignKey("roles.id"), nullable=False)
    scope_zone_id = Column(UUID(as_uuid=False), ForeignKey("zones.id"), nullable=True)
    assigned_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")
    scope_zone = relationship("Zone", foreign_keys=[scope_zone_id])
    __table_args__ = (UniqueConstraint("user_id", "role_id", "scope_zone_id", name="uq_user_role_scope"),)


class Zone(Base):
    __tablename__ = "zones"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name = Column(String(255), nullable=False)
    polygon = Column(JSONB)
    parent_zone_id = Column(UUID(as_uuid=False), ForeignKey("zones.id"))
    delivery_addresses = relationship("DeliveryAddress", back_populates="zone")


class DeliveryAddress(Base):
    __tablename__ = "delivery_addresses"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    line1 = Column(String(255), nullable=False)
    line2 = Column(String(255))
    city = Column(String(128))
    postal_code = Column(String(32))
    country = Column(String(2), default="US")
    lat = Column(Numeric(10, 7))
    lng = Column(Numeric(10, 7))
    zone_id = Column(UUID(as_uuid=False), ForeignKey("zones.id"))
    zone = relationship("Zone", back_populates="delivery_addresses")
    orders = relationship("Order", back_populates="delivery_address")


class Vehicle(Base):
    __tablename__ = "vehicles"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    plate = Column(String(32), nullable=False)
    type = Column(String(32), nullable=False)  # VAN, TRUCK, BIKE
    capacity_kg = Column(Numeric(10, 2), default=0)
    is_active = Column(Boolean, default=True)
    vehicle_assignments = relationship("VehicleAssignment", back_populates="vehicle")


class Driver(Base):
    __tablename__ = "drivers"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), unique=True, nullable=False)
    license_number = Column(String(64))
    phone = Column(String(32))
    status = Column(String(32), default="OFF_DUTY")  # AVAILABLE, BUSY, OFF_DUTY, BREAK
    current_location = Column(JSONB)
    last_availability_updated = Column(DateTime(timezone=True))
    auto_assign_eligible = Column(Boolean, default=True)
    user = relationship("User", back_populates="driver")
    vehicle_assignments = relationship("VehicleAssignment", back_populates="driver")
    deliveries = relationship("Delivery", back_populates="driver")
    routes = relationship("Route", back_populates="driver")


class VehicleAssignment(Base):
    __tablename__ = "vehicle_assignments"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    driver_id = Column(UUID(as_uuid=False), ForeignKey("drivers.id"), nullable=False)
    vehicle_id = Column(UUID(as_uuid=False), ForeignKey("vehicles.id"), nullable=False)
    assigned_from = Column(DateTime(timezone=True), nullable=False)
    assigned_until = Column(DateTime(timezone=True))
    driver = relationship("Driver", back_populates="vehicle_assignments")
    vehicle = relationship("Vehicle", back_populates="vehicle_assignments")
    __table_args__ = (UniqueConstraint("driver_id", "assigned_from", name="uq_driver_assigned_from"),)


class Order(Base):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    external_reference = Column(String(128), unique=True)
    delivery_address_id = Column(UUID(as_uuid=False), ForeignKey("delivery_addresses.id"), nullable=False)
    customer_name = Column(String(255))
    customer_phone = Column(String(32))
    customer_email = Column(String(255))
    status = Column(String(32), default="DRAFT")  # DRAFT, CONFIRMED, PREPARING, READY_FOR_PICKUP, CANCELLED
    requested_delivery_start = Column(DateTime(timezone=True))
    requested_delivery_end = Column(DateTime(timezone=True))
    total_weight_kg = Column(Numeric(10, 2), default=0)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    delivery_address = relationship("DeliveryAddress", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    delivery = relationship("Delivery", back_populates="order", uselist=False)


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    order_id = Column(UUID(as_uuid=False), ForeignKey("orders.id"), nullable=False)
    sku = Column(String(64))
    description = Column(String(255))
    quantity = Column(Integer, default=1)
    weight_kg = Column(Numeric(10, 2), default=0)
    order = relationship("Order", back_populates="order_items")


class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    order_id = Column(UUID(as_uuid=False), ForeignKey("orders.id"), unique=True, nullable=False)
    driver_id = Column(UUID(as_uuid=False), ForeignKey("drivers.id"))
    assigned_by = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    assigned_at = Column(DateTime(timezone=True))
    status = Column(String(32), default="PREPARATION")  # PREPARATION, IN_TRANSIT, DELIVERED, FAILED, RETURNED
    status_changed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    estimated_distance_km = Column(Numeric(10, 2))
    estimated_duration_mins = Column(Integer)
    estimated_arrival = Column(DateTime(timezone=True))
    route_snapshot = Column(JSONB)
    failure_reason = Column(Text)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    order = relationship("Order", back_populates="delivery")
    driver = relationship("Driver", back_populates="deliveries")
    status_history = relationship("DeliveryStatusHistory", back_populates="delivery", order_by="DeliveryStatusHistory.created_at")
    route_stops = relationship("RouteStop", back_populates="delivery")


class DeliveryStatusHistory(Base):
    __tablename__ = "delivery_status_history"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    delivery_id = Column(UUID(as_uuid=False), ForeignKey("deliveries.id"), nullable=False)
    status = Column(String(32), nullable=False)
    previous_status = Column(String(32))
    payload = Column(JSONB)
    changed_by = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    delivery = relationship("Delivery", back_populates="status_history")


class Route(Base):
    __tablename__ = "routes"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    driver_id = Column(UUID(as_uuid=False), ForeignKey("drivers.id"), nullable=False)
    planned_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(32), default="DRAFT")  # DRAFT, PUBLISHED, IN_PROGRESS, COMPLETED
    waypoints = Column(JSONB)
    total_stops = Column(Integer, default=0)
    total_distance_km = Column(Numeric(10, 2))
    total_duration_mins = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    driver = relationship("Driver", back_populates="routes")
    route_stops = relationship("RouteStop", back_populates="route", order_by="RouteStop.sequence")


class RouteStop(Base):
    __tablename__ = "route_stops"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    route_id = Column(UUID(as_uuid=False), ForeignKey("routes.id"), nullable=False)
    delivery_id = Column(UUID(as_uuid=False), ForeignKey("deliveries.id"), nullable=False)
    sequence = Column(Integer, nullable=False)
    estimated_arrival = Column(DateTime(timezone=True))
    status = Column(String(32), default="PENDING")  # PENDING, ARRIVED, COMPLETED, SKIPPED
    route = relationship("Route", back_populates="route_stops")
    delivery = relationship("Delivery", back_populates="route_stops")
    __table_args__ = (UniqueConstraint("route_id", "sequence", name="uq_route_sequence"),)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"))
    action = Column(String(64), nullable=False)
    resource_type = Column(String(64), nullable=False)
    resource_id = Column(UUID(as_uuid=False))
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    client_ip = Column(String(45))
    user_agent = Column(String(512))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    __table_args__ = (Index("ix_audit_resource", "resource_type", "resource_id"), Index("ix_audit_created", "created_at"),)


class Notification(Base):
    __tablename__ = "notifications"
    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    channel = Column(String(32), nullable=False)  # EMAIL, SMS, PUSH, IN_APP
    topic = Column(String(64), nullable=False)
    reference_id = Column(UUID(as_uuid=False))
    status = Column(String(32), default="PENDING")
    payload = Column(JSONB)
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
