from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from transformers import pipeline
import time
from app.core.jwt_auth import get_current_user
from app.sentiment_service import db

router = APIRouter()

SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
MAX_INPUT_CHARS = 6000

# load once at startup
try:
    sentiment_analyzer = pipeline("sentiment-analysis", model=SENTIMENT_MODEL)
except Exception as e:
    raise RuntimeError(f"Failed to load sentiment model {SENTIMENT_MODEL}: {e}")


class SentimentRequest(BaseModel):
    text: str = Field(..., description="Text to analyze sentiment for")

    @field_validator("text")
    def not_empty_and_truncate(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("Input text must not be empty.")
        if len(v) > MAX_INPUT_CHARS:
            v = v[:MAX_INPUT_CHARS]
        return v


@router.post("/analyze")
async def analyze_sentiment(req: SentimentRequest,
                            current_user: dict = Depends(get_current_user)):

    user_id = current_user["username"]
    start = time.time()

    try:
        result = sentiment_analyzer(req.text)
        # result example: [{"label": "POSITIVE", "score": 0.98}]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Sentiment inference failed")

    latency_ms = round((time.time() - start) * 1000, 2)
    label = result[0]["label"]
    score = float(result[0]["score"])

    # log to firestore
    db.log_sentiment(
        user_id=user_id,
        model=SENTIMENT_MODEL,
        input_text=req.text,
        label=label,
        score=score,
        latency_ms=latency_ms,
        input_chars=len(req.text),
    )

    return {
        "label": label,
        "score": score,
        "latency_ms": latency_ms,
        "model_name": SENTIMENT_MODEL,
        "input_chars": len(req.text),
    }


@router.get("/my-sentiments")
async def my_sentiments(limit: int = 20,
                        current_user: dict = Depends(get_current_user)):

    user_id = current_user["username"]
    items = db.get_sentiments_for_user(user_id=user_id, limit=limit)
    return {"user_id": user_id, "count": len(items), "items": items}
