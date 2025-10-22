import firebase_admin
from firebase_admin import credentials, firestore

#initialize firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate("./serviceAccountKey.json")  # path to your service account JSON
    firebase_admin.initialize_app(cred)

db = firestore.client(database_id="summarease-database")

def log_summary(model, input_text, summary, latency):
    doc = {
        #better timestamp
        "timestamp": firestore.firestore.SERVER_TIMESTAMP,
        "model": model,
        "input_text": input_text,
        "summary": summary,
        "input_chars": len(input_text),
        "summary_chars":len(summary),
        "latency": float(latency)
    }
    db.collection("summaries").add(doc)

    #check already stored data
    docs = db.collection("summaries").order_by("timestamp", direction=firestore.firestore.Query.DESCENDING).limit(1).stream()
    for d in docs:
        print(d.id, d.to_dict())
    print("Done")