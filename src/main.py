# this FastAPI app takes long text as input,
# summarizes it using a Hugging Face model,
# and returns the summary along with latency time.

from fastapi import FastAPI           # FastAPI: used to create the web API
from fastapi import HTTPException
from pydantic import BaseModel        # Pydantic: used for request validation
from pydantic import Field
from pydantic import field_validator
from transformers import pipeline     # Hugging Face pipeline: loads the AI model easily
import time                           # time: used to measure request duration

app = FastAPI(title="SummarEase API") # create the API instance with a visible title

MODEL_NAME = "facebook/bart-large-cnn"
MAX_INPUT_CHARS = 6000

# --- load the summarization model once at startup ---
summarizer = pipeline("summarization", model=MODEL_NAME)

# --- define what data we expect from the user ---

class SummarizeRequest(BaseModel):
    text: str = Field(..., description="Text to summarize")
    max_length: int = Field(150, ge=16, le=512, description="Max tokens in summary")
    min_length: int = Field(40, ge=8, le=256, description="Min tokens in summary")

    @field_validator("text")
    def not_empty_and_truncate(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Input text must not be empty.")
        # Truncate very long inputs to keep latency/cost bounded
        if len(v) > MAX_INPUT_CHARS:
            v = v[:MAX_INPUT_CHARS]
        return v

    @field_validator("max_length")
    def max_ge_min(cls, max_len, values):
        min_len = values.get("min_length", 40)
        if max_len < min_len:
            raise ValueError("max_length must be >= min_length.")
        return max_len

# lets you confirm the service is running (useful for testing and monitoring)
@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME}

# ---- Summarize ----
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
        # Bubble up as 500 with a safe message
        raise HTTPException(status_code=500, detail=f"Model inference failed: {type(e).__name__}")

    latency_ms = round((time.time() - start) * 1000, 2)
    summary_text = result[0]["summary_text"]

    return {
        "summary": summary_text,
        "latency_ms": latency_ms,
        "model_name": MODEL_NAME,
        "input_chars": len(req.text),
        "output_chars": len(summary_text)
    }
