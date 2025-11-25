FROM python:3.10-slim

WORKDIR /app

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Upgrade pip
RUN python -m pip install --upgrade pip

# Copy requirements file
COPY app/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download models to reduce cold start time
RUN python -c "from transformers import pipeline; pipeline('summarization', model='facebook/bart-large-cnn')"
RUN python -c "from transformers import pipeline; pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')"

# Copy the entire app directory
COPY app/ ./app/

# Expose port (Cloud Run will override this with PORT env var)
EXPOSE 8080

# Run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}