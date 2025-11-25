from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from transformers import pipeline
import time
from core.jwt_auth import get_current_user
from sentiment_service import db

router = APIRouter()

SENTIMENT_MODEL = "SamLowe/roberta-base-go_emotions"
MAX_INPUT_CHARS = 6000

# load sentiment_model at startup
try:
    emotion_analyzer = pipeline(
        "text-classification",
        model=SENTIMENT_MODEL,
        top_k=None  # return ALL labels with scores (new HF versions)
    )
except TypeError:
    # fallback for older transformers versions
    emotion_analyzer = pipeline(
        "text-classification",
        model=SENTIMENT_MODEL,
        return_all_scores=True
    )
except Exception:
    raise RuntimeError(f"Failed to load emotion model {SENTIMENT_MODEL}: {e}")

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
        result = emotion_analyzer(req.text, truncation=True)

        # Two possible shapes depending on transformers version:
        # Shape A (top_k=None): [[{"label": "...", "score": ...}, ...]]
        # Shape B (return_all_scores=True): [[{"label": "...", "score": ...}, ...]]
        scores_list = result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Sentiment inference failed")

    latency_ms = round((time.time() - start) * 1000, 2)

    # Convert to dict: {"joy": 0.7, "sadness": 0.2, ...}
    emotions = {x["label"].lower(): float(x["score"]) for x in scores_list}

    # Top emotion
    top_label = max(emotions, key=emotions.get)
    top_score = emotions[top_label]

    # log to firestore
    db.log_sentiment(
        user_id=user_id,
        model=SENTIMENT_MODEL,
        input_text=req.text,
        top_label=top_label,
        top_score=top_score,
        emotions=emotions,
        latency_ms=latency_ms,
        input_chars=len(req.text),
    )

    return {
        "top_label": top_label,
        "top_score": top_score,
        "emotions": emotions,
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
