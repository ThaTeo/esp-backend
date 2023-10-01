import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def get_firestore():
    return firestore.client(
        firebase_admin.initialize_app(
            credentials.Certificate('./app/credentials.json')
        ))
