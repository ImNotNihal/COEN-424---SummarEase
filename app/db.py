import firebase_admin
from firebase_admin import credentials, firestore
import os, time

cred = credentials.Certificate("firebase-key.json")  # path to your service account JSON
firebase_admin.initialize_app(cred)
db = firestore.client()

def log_summary(text, summary, latency):
    doc = {
        "timestamp": time.time(),
        "input_length": len(text),
        "summary_length": len(summary),
        "latency": latency
    }
    db.collection("summaries").add(doc)
