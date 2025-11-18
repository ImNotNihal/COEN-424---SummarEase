#FROM python:3.10-slim
#
#WORKDIR /summary_service
#RUN python -m pip install --upgrade pip
#
#COPY summary_service/requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
#
#COPY summary_service/ .
#
#CMD ["uvicorn", "main:summary_service", "--host", "0.0.0.0", "--port", "8080"]

FROM python:3.10-slim

WORKDIR /app

# Force amd64 build later from the CLI, we’ll get to that
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Upgrade pip
RUN python -m pip install --upgrade pip

# Copy requirements first
COPY summary_service/requirements.txt .

# Install deps
RUN pip install --no-cache-dir -r requirements.txt

# add after pip install
RUN python -c "from transformers import pipeline; pipeline('summarization', model='facebook/bart-large-cnn')"

# Copy summary_service code
COPY summary_service/ .

# Port for Cloud Run
ENV PORT=8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
