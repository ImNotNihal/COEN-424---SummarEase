# FastAPI app for summarizing text using Hugging Face
# Returns summary along with latency metrics

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from transformers import pipeline
import time
import db as db


app = FastAPI(title="SummarEase API")

MODEL_NAME = "facebook/bart-large-cnn"
MAX_INPUT_CHARS = 6000  # truncate very long inputs

# --- load the model once at startup ---
try:
    summarizer = pipeline("summarization", model=MODEL_NAME)
except Exception as e:
    raise RuntimeError(f"Failed to load model {MODEL_NAME}: {e}")

# --- request model ---
class SummarizeRequest(BaseModel):
    text: str = Field(..., description="Text to summarize")
    max_length: int = Field(150, ge=16, le=512)
    min_length: int = Field(40, ge=8, le=256)

    @field_validator("text")
    def not_empty_and_truncate(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Input text must not be empty.")
        if len(v) > 6000:
            v = v[:6000]
        return v

    @field_validator("max_length")
    def max_ge_min(cls, max_len: int, info: ValidationInfo):
        min_len = info.data.get("min_length", 40)  # <-- use info.data instead of values
        if max_len < min_len:
            raise ValueError("max_length must be >= min_length.")
        return max_len

# --- health check endpoint ---
@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME}

# --- summarize endpoint ---
@app.post("/summarize")
async def summarize(req: SummarizeRequest):
    start = time.time()
    try:
        result = summarizer(
            req.text,
            max_length=req.max_length,
            min_length=req.min_length,
            do_sample=False
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {type(e).__name__}")

    latency_ms = round((time.time() - start) * 1000, 2)
    summary_text = result[0]["summary_text"]

    #log data into database (input_text, summary, latency)
    db.log_summary(MODEL_NAME, req.text, summary_text, latency_ms)

    return {
        "summary": summary_text,
        "latency_ms": latency_ms,
        "model_name": MODEL_NAME,
        "input_chars": len(req.text),
        "output_chars": len(summary_text)
    }
