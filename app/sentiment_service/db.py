from datetime import datetime
from google.cloud.firestore_v1 import Query, FieldFilter
from app.core.firebase import db

COLLECTION = "sentiments"

def log_sentiment(user_id: str, model: str, input_text: str,
                  label: str, score: float,
                  latency_ms: float, input_chars: int):
    doc = {
        "user_id": user_id,
        "timestamp": datetime.utcnow(),
        "model": model,
        "input_text": input_text,
        "label": label,
        "score": score,
        "latency_ms": latency_ms,
        "input_chars": input_chars,
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
