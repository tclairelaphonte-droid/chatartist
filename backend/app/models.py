import enum
import uuid

from sqlalchemy import (
    Column, String, Text, DateTime, ForeignKey, Enum, Boolean,
    UniqueConstraint, CheckConstraint, func, JSON,
)
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class UserRole(str, enum.Enum):
    fan = "fan"
    manager = "manager"
    admin = "admin"


class SenderType(str, enum.Enum):
    fan = "fan"
    manager = "manager"


class User(Base):
    """Compte : fan, manager (client) ou admin (plateforme)."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    username = Column(String(60), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    avatar_url = Column(String(500), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.fan)
    # Suspendu par l'admin → login refusé jusqu'au déblocage
    is_blocked = Column(Boolean, nullable=False, default=False)
    reset_token = Column(String(120), nullable=True, index=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversations = relationship(
        "Conversation", back_populates="fan", cascade="all, delete-orphan"
    )
    artists = relationship(
        "Artist", back_populates="manager", cascade="all, delete-orphan"
    )


class Artist(Base):
    __tablename__ = "artists"

    id = Column(String(36), primary_key=True, default=gen_uuid)

    manager_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    slug = Column(String(60), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    genre = Column(String(120), nullable=True)
    bio_short = Column(String(300), nullable=True)
    bio_full = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    cover_url = Column(String(500), nullable=True)

    is_published = Column(Boolean, nullable=False, default=True)

    gallery = Column(JSON, nullable=True)
    tracks = Column(JSON, nullable=True)
    clips = Column(JSON, nullable=True)
    news = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    manager = relationship("User", back_populates="artists")
    conversations = relationship(
        "Conversation", back_populates="artist", cascade="all, delete-orphan"
    )


class Conversation(Base):
    """
    Un fil unique par couple (fan, artiste).
    trashed_at : corbeille côté manager (None = inbox).
    """
    __tablename__ = "conversations"
    __table_args__ = (UniqueConstraint("fan_id", "artist_id", name="uq_fan_artist"),)

    id = Column(String(36), primary_key=True, default=gen_uuid)
    fan_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    artist_id = Column(String(36), ForeignKey("artists.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    trashed_at = Column(DateTime(timezone=True), nullable=True, index=True)

    fan = relationship("User", back_populates="conversations")
    artist = relationship("Artist", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint(
            "text IS NOT NULL OR image_url IS NOT NULL",
            name="ck_message_has_content",
        ),
    )

    id = Column(String(36), primary_key=True, default=gen_uuid)
    conversation_id = Column(
        String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False
    )
    sender_type = Column(Enum(SenderType), nullable=False)
    text = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    read_by_manager = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    conversation = relationship("Conversation", back_populates="messages")