from fastapi import FastAPI
from auth_service.router import router as auth_router
from summary_service.router import router as summary_router
from sentiment_service.router import router as sentiment_router

app = FastAPI(title="SummarEase API")

# link router for auth
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
# link router for summary
app.include_router(summary_router, prefix="/summary", tags=["Summarize"])
#sentiment analysis
app.include_router(sentiment_router, prefix="/sentiment", tags=["Sentiment"])

@app.get("/")
def root():
    return {"message": "SummarEase API is running; Go to /docs to see the Routes {0.0}"}