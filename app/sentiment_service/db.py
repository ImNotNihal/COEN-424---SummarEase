from datetime import datetime
from google.cloud.firestore_v1 import Query, FieldFilter
from core.firebase import db
from firebase_admin import firestore

COLLECTION = "sentiments"

def log_sentiment(user_id: str, model: str, input_text: str,
                  top_label: str, top_score: float, emotions:str,
                  latency_ms: float, input_chars: int):
    doc = {
        "user_id": user_id,
        "model": model,
        "input_text": input_text,
        "top_label": top_label,
        "top_score": float(top_score),
        "emotions": emotions,  # dict of all scores
        "latency_ms": float(latency_ms),
        "input_chars": int(input_chars),
        "timestamp": firestore.firestore.SERVER_TIMESTAMP,
    }
    db.collection(COLLECTION).add(doc)

def get_sentiments_for_user(user_id: str, limit: int = 20):
    query = (
        db.collection(COLLECTION)
          .where(filter=FieldFilter("user_id", "==", user_id))
          .order_by("timestamp", direction=Query.DESCENDING)
          .limit(limit)
    )
    results = []
    for doc in query.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results
