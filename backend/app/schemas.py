from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------

class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=60)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    avatar_url: Optional[str] = None
    role: Literal["fan", "manager", "admin"]
    is_blocked: bool = False

    class Config:
        from_attributes = True


class ForgotPasswordIn(BaseModel):
    email: EmailStr


class ForgotPasswordOut(BaseModel):
    message: str
    dev_reset_token: Optional[str] = None


class ResetPasswordIn(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


# ---------- Admin ----------

class ManagerAdminOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    is_blocked: bool = False
    created_at: Optional[datetime] = None
    artist_count: int = 0

    class Config:
        from_attributes = True


# ---------- Artists ----------

class ArtistOut(BaseModel):
    id: str
    slug: str
    name: str
    genre: Optional[str] = None

    # Français (par défaut)
    bio_short: Optional[str] = None
    bio_full: Optional[str] = None

    # Multi-langues
    bio_short_en: Optional[str] = None
    bio_full_en: Optional[str] = None
    bio_short_it: Optional[str] = None
    bio_full_it: Optional[str] = None
    bio_short_de: Optional[str] = None
    bio_full_de: Optional[str] = None
    bio_short_es: Optional[str] = None
    bio_full_es: Optional[str] = None
    bio_short_fi: Optional[str] = None
    bio_full_fi: Optional[str] = None

    avatar_url: Optional[str] = None
    cover_url: Optional[str] = None
    is_published: bool = True
    manager_id: Optional[str] = None
    gallery: Optional[list[str]] = None
    tracks: Optional[list[list[str]]] = None
    clips: Optional[list[list[str]]] = None
    news: Optional[list[list[str]]] = None
    # Non-lus fan → manager (liste dashboard)
    unread_count: int = 0

    class Config:
        from_attributes = True


class ArtistWithCount(ArtistOut):
    conversation_count: int = 0
    message_count: int = 0


class ArtistCreateIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=60)
    genre: Optional[str] = Field(default=None, max_length=120)

    bio_short: Optional[str] = Field(default=None, max_length=300)
    bio_full: Optional[str] = None

    bio_short_en: Optional[str] = Field(default=None, max_length=300)
    bio_full_en: Optional[str] = None
    bio_short_it: Optional[str] = Field(default=None, max_length=300)
    bio_full_it: Optional[str] = None
    bio_short_de: Optional[str] = Field(default=None, max_length=300)
    bio_full_de: Optional[str] = None
    bio_short_es: Optional[str] = Field(default=None, max_length=300)
    bio_full_es: Optional[str] = None
    bio_short_fi: Optional[str] = Field(default=None, max_length=300)
    bio_full_fi: Optional[str] = None

    avatar_url: Optional[str] = Field(default=None, max_length=500)
    cover_url: Optional[str] = Field(default=None, max_length=500)
    is_published: bool = True
    gallery: Optional[list[str]] = None
    tracks: Optional[list[list[str]]] = None
    clips: Optional[list[list[str]]] = None
    news: Optional[list[list[str]]] = None


class ArtistUpdateIn(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    slug: Optional[str] = Field(default=None, min_length=1, max_length=60)
    genre: Optional[str] = Field(default=None, max_length=120)

    bio_short: Optional[str] = Field(default=None, max_length=300)
    bio_full: Optional[str] = None

    bio_short_en: Optional[str] = Field(default=None, max_length=300)
    bio_full_en: Optional[str] = None
    bio_short_it: Optional[str] = Field(default=None, max_length=300)
    bio_full_it: Optional[str] = None
    bio_short_de: Optional[str] = Field(default=None, max_length=300)
    bio_full_de: Optional[str] = None
    bio_short_es: Optional[str] = Field(default=None, max_length=300)
    bio_full_es: Optional[str] = None
    bio_short_fi: Optional[str] = Field(default=None, max_length=300)
    bio_full_fi: Optional[str] = None

    avatar_url: Optional[str] = Field(default=None, max_length=500)
    cover_url: Optional[str] = Field(default=None, max_length=500)
    is_published: Optional[bool] = None
    gallery: Optional[list[str]] = None
    tracks: Optional[list[list[str]]] = None
    clips: Optional[list[list[str]]] = None
    news: Optional[list[list[str]]] = None


# ---------- Conversations & messages ----------

class MessageOut(BaseModel):
    id: str
    sender_type: Literal["fan", "manager"]
    text: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: str
    artist_id: str
    artist_name: str
    fan_id: str
    fan_username: str
    fan_avatar_url: Optional[str] = None
    last_message: Optional[MessageOut] = None
    unread_count: int = 0
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationDetailOut(BaseModel):
    id: str
    artist: ArtistOut
    messages: list[MessageOut]

    class Config:
        from_attributes = True


class SendMessageIn(BaseModel):
    text: Optional[str] = Field(default=None, max_length=4000)
    image_url: Optional[str] = None