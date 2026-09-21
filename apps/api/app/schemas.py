import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------------------------------------------------------
# USUARIOS & AUTENTICACION
# ---------------------------------------------------------

class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = "host"
    expires_in: int


class GuestEnterRequest(BaseModel):
    pin: str = Field(min_length=4, max_length=10)


class GuestAuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = "guest"
    event_slug: str


# ---------------------------------------------------------
# EVENTOS
# ---------------------------------------------------------

class EventBase(BaseModel):
    title: str
    event_date: datetime
    event_type: str = "boda"
    tier: str = "sincronia_total"
    location_name: Optional[str] = None
    location_address: Optional[str] = None
    location_maps_url: Optional[str] = None
    location_waze_url: Optional[str] = None
    itinerary: Optional[str] = None
    gift_registry_info: Optional[str] = None
    dress_code: Optional[str] = None


class EventCreate(EventBase):
    slug: str = Field(min_length=3, max_length=100)
    pin_code: str = Field(min_length=4, max_length=10)
    storage_limit_bytes: Optional[int] = 16106127360  # 15 GB


class EventUpdate(BaseModel):
    title: Optional[str] = None
    event_date: Optional[datetime] = None
    location_name: Optional[str] = None
    location_address: Optional[str] = None
    location_maps_url: Optional[str] = None
    location_waze_url: Optional[str] = None
    itinerary: Optional[str] = None
    gift_registry_info: Optional[str] = None
    dress_code: Optional[str] = None
    pin_code: Optional[str] = None
    is_active: Optional[bool] = None


class EventRead(EventBase):
    id: uuid.UUID
    host_id: uuid.UUID
    slug: str
    pin_code: str
    storage_limit_bytes: int
    storage_used_bytes: int
    is_active: bool
    expires_at: Optional[datetime]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class EventPublicVocatus(BaseModel):
    slug: str
    title: str
    event_date: datetime
    event_type: str
    location_name: Optional[str] = None
    location_address: Optional[str] = None
    location_maps_url: Optional[str] = None
    location_waze_url: Optional[str] = None
    itinerary: Optional[str] = None
    gift_registry_info: Optional[str] = None
    dress_code: Optional[str] = None
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------
# RSVP & INVITADOS (VOCATUS)
# ---------------------------------------------------------

class RSVPGuestBase(BaseModel):
    guest_name: str
    phone_or_email: Optional[str] = None
    allocated_passes: int = 1


class RSVPGuestCreate(RSVPGuestBase):
    event_id: uuid.UUID


class RSVPGuestSearchItem(BaseModel):
    id: uuid.UUID
    guest_name: str
    allocated_passes: int
    confirmed_passes: int
    status: str
    model_config = ConfigDict(from_attributes=True)


class RSVPConfirmSubmit(BaseModel):
    guest_id: Optional[uuid.UUID] = None
    guest_name: Optional[str] = None
    confirmed_passes: int = Field(default=1, ge=0)
    status: str = Field(default="confirmed", pattern="^(confirmed|declined)$")
    dietary_restrictions: Optional[str] = None
    message: Optional[str] = None


class RSVPGuestRead(RSVPGuestBase):
    id: uuid.UUID
    event_id: uuid.UUID
    confirmed_passes: int
    status: str
    dietary_restrictions: Optional[str]
    message: Optional[str]
    confirmed_at: Optional[datetime]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------
# MEDIA & BOVEDA (ANIMUS)
# ---------------------------------------------------------

class BatchPresignedFile(BaseModel):
    filename: str
    size_bytes: int = Field(gt=0)
    content_type: str


class BatchPresignedRequest(BaseModel):
    files: List[BatchPresignedFile]


class PresignedUrlItem(BaseModel):
    file_id: uuid.UUID
    filename: str
    upload_url: str
    r2_key: str
    thumb_upload_url: Optional[str] = None
    thumb_r2_key: Optional[str] = None


class BatchPresignedResponse(BaseModel):
    items: List[PresignedUrlItem]


class MediaItemConfirm(BaseModel):
    id: uuid.UUID
    r2_key: str
    thumb_r2_key: Optional[str] = None
    filename: str
    content_type: str
    size_bytes: int
    guest_author: Optional[str] = None


class AnimusEventInfo(BaseModel):
    slug: str
    title: str
    event_date: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class MediaItemRead(BaseModel):
    id: uuid.UUID
    event_id: uuid.UUID
    r2_key: str
    thumb_r2_key: Optional[str] = None
    filename: str
    content_type: str
    size_bytes: int
    guest_author: Optional[str] = None
    moderation_status: str
    is_favorite: bool
    created_at: datetime
    url: Optional[str] = None
    thumb_url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class MediaModerateRequest(BaseModel):
    moderation_status: Optional[str] = Field(None, pattern="^(approved|hidden|rejected)$")
    is_favorite: Optional[bool] = None


# ---------------------------------------------------------
# ZIP JOBS
# ---------------------------------------------------------

class ZipJobCreate(BaseModel):
    event_id: uuid.UUID


class ZipJobRead(BaseModel):
    id: uuid.UUID
    event_id: uuid.UUID
    status: str
    r2_zip_key: Optional[str]
    zip_size_bytes: Optional[int]
    download_url: Optional[str]
    expires_at: Optional[datetime]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------
# PANEL DE ADMINISTRACION (METRICAS)
# ---------------------------------------------------------

class AdminDashboardMetrics(BaseModel):
    event: EventRead
    total_allocated_passes: int
    total_confirmed_passes: int
    total_declined_guests: int
    total_pending_guests: int
    total_photos_count: int
    storage_used_bytes: int
    storage_limit_bytes: int
    storage_usage_percent: float
