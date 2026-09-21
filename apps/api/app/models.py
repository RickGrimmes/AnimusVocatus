import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relaciones
    events: Mapped[List["Event"]] = relationship(
        "Event",
        back_populates="host",
        cascade="all, delete-orphan",
    )


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    host_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    event_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="boda",
    )
    tier: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="sincronia_total",
    )
    pin_code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    storage_limit_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=16106127360,  # 15 GB por defecto
    )
    storage_used_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    location_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    location_address: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    location_maps_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    location_waze_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    itinerary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    gift_registry_info: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    dress_code: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relaciones
    host: Mapped["User"] = relationship(
        "User",
        back_populates="events",
    )
    guests: Mapped[List["RSVPGuest"]] = relationship(
        "RSVPGuest",
        back_populates="event",
        cascade="all, delete-orphan",
    )
    media_items: Mapped[List["MediaItem"]] = relationship(
        "MediaItem",
        back_populates="event",
        cascade="all, delete-orphan",
    )
    zip_jobs: Mapped[List["ZipJob"]] = relationship(
        "ZipJob",
        back_populates="event",
        cascade="all, delete-orphan",
    )


class RSVPGuest(Base):
    __tablename__ = "rsvp_guests"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    guest_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    phone_or_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    allocated_passes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    confirmed_passes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",  # pending, confirmed, declined
    )
    dietary_restrictions: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relaciones
    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="guests",
    )


class MediaItem(Base):
    __tablename__ = "media_items"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    r2_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    thumb_r2_key: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    guest_author: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    moderation_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="approved",  # approved, hidden, rejected
    )
    is_favorite: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relaciones
    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="media_items",
    )


class ZipJob(Base):
    __tablename__ = "zip_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",  # pending, processing, ready, failed
    )
    r2_zip_key: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    zip_size_bytes: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
    )
    download_url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relaciones
    event: Mapped["Event"] = relationship(
        "Event",
        back_populates="zip_jobs",
    )
