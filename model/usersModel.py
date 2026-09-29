from google.api_core.exceptions import AlreadyExists
from model.dbAdminInitializer import firestoreDB

users = firestoreDB.collection('users')


def createUser(username, passwordHash, salt):
    #Creates users/{username}. Returns False if that username already exists.
    #create() (unlike set()) fails if the document exists, so Firestore itself guarantees usernames are unique, even if two people register at once.
    try:
        users.document(username).create({
            'username': username,
            'passwordHash': passwordHash,
            'salt': salt,
        })
        return True
    except AlreadyExists:
        return False


def getUser(username):
    doc = users.document(username).get()
    return doc.to_dict() if doc.exists else None