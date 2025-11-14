import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents

app = FastAPI(title="Social Creator Platform API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- Schemas (importing for type hints only) ---------
from schemas import (
    User, Post, Comment, Like, Message, Group, Notification,
    SubscriptionPlan, Subscription, Payment, Stream, AudioRoom,
    AnalyticsEvent
)

# --------- Helpers ---------
class IdResponse(BaseModel):
    id: str

# --------- Health ---------
@app.get("/")
def root():
    return {"service": "creator-platform", "status": "ok"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set"
            response["database_name"] = getattr(db, 'name', '✅ Connected')
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:20]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

# --------- Users ---------
@app.post("/users", response_model=IdResponse)
def create_user(user: User):
    new_id = create_document("user", user)
    return {"id": new_id}

@app.get("/users")
def list_users():
    return get_documents("user", {}, 50)

# --------- Posts (with premium flag) ---------
@app.post("/posts", response_model=IdResponse)
def create_post(post: Post):
    new_id = create_document("post", post)
    return {"id": new_id}

@app.get("/posts")
def list_posts(tag: Optional[str] = None, author_id: Optional[str] = None):
    query = {}
    if tag:
        query["tags"] = {"$in": [tag]}
    if author_id:
        query["author_id"] = author_id
    return get_documents("post", query, 100)

# --------- Comments & Likes ---------
@app.post("/comments", response_model=IdResponse)
def add_comment(comment: Comment):
    new_id = create_document("comment", comment)
    return {"id": new_id}

@app.post("/likes", response_model=IdResponse)
def add_like(like: Like):
    new_id = create_document("like", like)
    return {"id": new_id}

# --------- Messaging ---------
@app.post("/messages", response_model=IdResponse)
def send_message(msg: Message):
    new_id = create_document("message", msg)
    return {"id": new_id}

@app.get("/messages")
def get_messages(user_id: str, with_user: Optional[str] = None):
    q = {"$or": [{"sender_id": user_id}, {"recipient_id": user_id}]}
    if with_user:
        q = {"$or": [
            {"sender_id": user_id, "recipient_id": with_user},
            {"sender_id": with_user, "recipient_id": user_id}
        ]}
    return get_documents("message", q, 200)

# --------- Subscriptions & Payments (mock provider) ---------
@app.post("/plans", response_model=IdResponse)
def create_plan(plan: SubscriptionPlan):
    new_id = create_document("subscriptionplan", plan)
    return {"id": new_id}

@app.post("/subscriptions", response_model=IdResponse)
def create_subscription(sub: Subscription):
    # In real life, verify payment provider webhook before activation
    new_id = create_document("subscription", sub)
    return {"id": new_id}

@app.post("/payments", response_model=IdResponse)
def create_payment(payment: Payment):
    # Minimal mock payment recording
    new_id = create_document("payment", payment)
    return {"id": new_id}

# --------- Notifications ---------
@app.post("/notifications", response_model=IdResponse)
def create_notification(n: Notification):
    new_id = create_document("notification", n)
    return {"id": new_id}

@app.get("/notifications")
def list_notifications(user_id: str):
    return get_documents("notification", {"user_id": user_id}, 100)

# --------- Streams & Audio Rooms ---------
@app.post("/streams", response_model=IdResponse)
def create_stream(s: Stream):
    new_id = create_document("stream", s)
    return {"id": new_id}

@app.post("/audio-rooms", response_model=IdResponse)
def create_audio_room(r: AudioRoom):
    new_id = create_document("audioroom", r)
    return {"id": new_id}

# --------- Simple search & recommendations (mock) ---------
class SearchQuery(BaseModel):
    q: str

@app.post("/search")
def search(payload: SearchQuery):
    q = payload.q
    # naive search over posts text and tags
    return get_documents("post", {"$or": [
        {"text": {"$regex": q, "$options": "i"}},
        {"tags": {"$in": [q]}}
    ]}, 50)

@app.get("/recommendations")
def recommendations(user_id: Optional[str] = None):
    # naive: return latest public posts; a real system would use embeddings/CF
    return get_documents("post", {"visibility": {"$in": ["public","followers"]}}, 20)

# --------- Analytics ---------
@app.post("/analytics", response_model=IdResponse)
def track(event: AnalyticsEvent):
    new_id = create_document("analyticsevent", event)
    return {"id": new_id}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
