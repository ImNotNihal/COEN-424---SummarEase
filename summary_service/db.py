import os
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import Query, FieldFilter

# oblige de faire ca, sinon ca trouve pas le fichier
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_KEY_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")

#initialize firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_KEY_PATH)  # path to your service account JSON
    firebase_admin.initialize_app(cred)

db = firestore.client(database_id="summarease-database")

def log_summary(user_id, model, input_text, summary, input_tokens, output_tokens,latency):
    doc = {
        "user_id": user_id,
        #better timestamp
        "timestamp": firestore.firestore.SERVER_TIMESTAMP,
        "model": model,
        "input_text": input_text,
        "summary": summary,
        "input_tokens": input_tokens,
        "summary_tokens":output_tokens,
        "latency": float(latency)
    }
    db.collection("summaries").add(doc)

    #check already stored data
    docs = db.collection("summaries").order_by("timestamp", direction=firestore.firestore.Query.DESCENDING).limit(1).stream()
    for d in docs:
        print(d.id, d.to_dict())
    print("Done")


# get summary by user / only authenticated user can get its summaries
def get_summaries_for_user(user_id: str, limit: int = 20):

    query = (
        db.collection("summaries")
        .where(filter=FieldFilter("user_id", "==", user_id))
        .order_by("timestamp", direction=Query.DESCENDING)
        .limit(limit)
    )

    docs = query.stream()
    results = []
    for d in docs:
        item = d.to_dict()
        item["id"] = d.id
        results.append(item)

    print(results)
    return results