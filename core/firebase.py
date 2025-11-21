from firebase_admin import credentials, firestore, initialize_app
import firebase_admin
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

SERVICE_KEY_PATH = os.path.join(PROJECT_ROOT, "serviceAccountKey.json")

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_KEY_PATH)
    firebase_admin.initialize_app(cred)

db = firestore.client(database_id="summarease-database")
