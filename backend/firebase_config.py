import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("calendar-firebase-adminsdk.json")
firebase_admin.initialize_app(cred)

db = firestore.client()