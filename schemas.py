"""
Database Schemas for the Social Creator Platform

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name (e.g., User -> "user").

These schemas are used for validation in request bodies and to keep a consistent
shape for documents stored via the helper functions in database.py
"""
from __future__ import annotations
from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field, HttpUrl

# Core user and profile
class ProfileSettings(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    banner_url: Optional[HttpUrl] = None
    theme: Optional[str] = Field(default="light")
    links: Optional[List[HttpUrl]] = None
    privacy_level: Literal["public", "followers", "subscribers", "private"] = "public"

class User(BaseModel):
    username: str = Field(..., description="Unique handle")
    email: str = Field(..., description="Email address")
    name: Optional[str] = None
    settings: Optional[ProfileSettings] = None
    is_creator: bool = True
    verified: bool = False

# Monetization
class SubscriptionPlan(BaseModel):
    creator_id: str
    title: str
    price_cents: int = Field(..., ge=0)
    currency: str = Field(default="USD")
    benefits: List[str] = []
    tier: Literal["bronze","silver","gold","platinum"] = "bronze"

class Subscription(BaseModel):
    creator_id: str
    subscriber_id: str
    plan_id: str
    status: Literal["active","canceled","past_due"] = "active"
    renews_at: Optional[str] = None

class Payment(BaseModel):
    user_id: str
    amount_cents: int
    currency: str = "USD"
    purpose: Literal["subscription","tip","purchase"] = "subscription"
    provider: Literal["stripe","paypal","mock"] = "mock"
    status: Literal["initiated","succeeded","failed"] = "initiated"
    metadata: Optional[Dict[str, str]] = None

# Content
class DRMPolicy(BaseModel):
    watermark: bool = True
    expire_seconds: Optional[int] = 3600
    allow_download: bool = False

class Post(BaseModel):
    author_id: str
    content_type: Literal["text","image","short_video","live_stream","audio"]
    text: Optional[str] = None
    media_url: Optional[HttpUrl] = None
    thumbnail_url: Optional[HttpUrl] = None
    tags: List[str] = []
    is_premium: bool = False
    required_tier: Optional[str] = None
    drm: Optional[DRMPolicy] = None
    visibility: Literal["public","followers","subscribers","private"] = "public"

class Comment(BaseModel):
    post_id: str
    author_id: str
    text: str

class Like(BaseModel):
    post_id: str
    user_id: str

# Social & messaging
class Message(BaseModel):
    sender_id: str
    recipient_id: str
    body: str
    thread_id: Optional[str] = None

class Group(BaseModel):
    owner_id: str
    name: str
    description: Optional[str] = None
    members: List[str] = []

class Notification(BaseModel):
    user_id: str
    type: Literal["like","comment","message","subscription","system"]
    title: str
    body: Optional[str] = None
    read: bool = False

# Live & audio
class Stream(BaseModel):
    creator_id: str
    title: str
    status: Literal["scheduled","live","ended"] = "scheduled"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    access: Literal["public","subscribers","pay_per_view"] = "public"

class AudioRoom(BaseModel):
    host_id: str
    topic: str
    status: Literal["scheduled","live","ended"] = "scheduled"
    speakers: List[str] = []

# Analytics
class AnalyticsEvent(BaseModel):
    user_id: Optional[str] = None
    event_name: str
    properties: Dict[str, str] = {}

# Minimal search index schema
class SearchIndex(BaseModel):
    doc_type: Literal["user","post","group"]
    ref_id: str
    tokens: List[str]
