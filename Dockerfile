# ✅ Official PyTorch image (CPU-only by default)
FROM pytorch/pytorch:latest

# Set working directory
WORKDIR /app

# Copy requirements first to leverage caching
COPY app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt uvicorn fastapi

# Copy app code
COPY app/ .

# Expose FastAPI port
EXPOSE 8080

# Launch the FastAPI app
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
