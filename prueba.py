import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("C:\Users\HOME\Desktop\prueba1.txt")
firebase_admin.initialize_app(cred)

db = firestore.client() 

# Ejemplo: obtener datos de una colección
docs = db.collection("usuarios").stream()
for doc in docs:
    print(f"{doc.id} => {doc.to_dict()}")