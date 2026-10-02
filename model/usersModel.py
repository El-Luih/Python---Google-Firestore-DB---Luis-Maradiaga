# Firestore access for user accounts.
# Username is the document ID, so lookups are fast and duplicate users are blocked.

from google.api_core.exceptions import AlreadyExists
from model.dbAdminInitializer import firestoreDB

users = firestoreDB.collection('users')


# Creates a new user only if the username is not already taken.
def createUser(username, passwordHash, salt):
    try:
        users.document(username).create({
            'username': username,
            'passwordHash': passwordHash,
            'salt': salt,
        })
        return True
    except AlreadyExists:
        return False


# Reads one user document by username.
def getUser(username):
    doc = users.document(username).get()
    return doc.to_dict() if doc.exists else None