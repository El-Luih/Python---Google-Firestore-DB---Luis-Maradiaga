# Initializes Firebase Admin and creates the Firestore client.
# This is the app's main connection to Firestore.

import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Store the service account JSON next to the app code and resolve it from the
# module directory so the project does not depend on the current working directory.
dbCredentials = credentials.Certificate(os.path.join(BASE_DIR, "dbKey.json"))

firebase_admin.initialize_app(dbCredentials)

firestoreDB = firestore.client()