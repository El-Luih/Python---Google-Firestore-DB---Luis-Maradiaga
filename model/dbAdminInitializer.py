import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dbCredentials = credentials.Certificate(os.path.join(BASE_DIR, "dbKey.json")) #Could have used a relative path. Used the os file path finder to comply with industry standards.

firebase_admin.initialize_app(dbCredentials)

firestoreDB = firestore.client()