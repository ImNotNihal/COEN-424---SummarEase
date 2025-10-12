# COEN-424---SummarEase - A Cloud-Based Text Summarization Service

Overview
- SummarEase is a cloud-hosted text summarization platform designed to automatically generate concise summaries from long documents, reports, or articles. The service leverages natural language processing (NLP) models to help users quickly extract key insights from large volumes of text which reduces information overload and improves productivity.

Objectives
- Provide an AI-driven API that can summarize text efficiently and accurately.
- Deploy a scalable cloud-based service accessible from anywhere.
- Store and track summarization results and performance data using a NoSQL database.
- Measure and analyze latency to evaluate model and system performance.

Technical Implementation
- Frontend: REST API built with FastAPI, accessible via Swagger UI.
- AI Model: facebook/bart-large-cnn (Hugging Face Transformers) is a pre-trained summarization model developed by Meta AI.
- Google Cloud Run is a serverless deployment to ensure automatic scaling and zero infrastructure management.
- Firestore (Firebase) is used for logging user requests, summaries, and performance metrics.
- GitHub for collaboration and CI/CD integration.
- The system records and reports latency per request, enabling ongoing optimization and reliability tracking.

Architecture Summary
- User sends a POST request with a text body to /summarize.
- The FastAPI backend forwards the text to the Hugging Face summarization model.
- The model outputs a concise summary (e.g., 3–5 sentences).
- Firestore stores input length, output length, and processing latency.
- The summarized text and timing metrics are returned to the user.
