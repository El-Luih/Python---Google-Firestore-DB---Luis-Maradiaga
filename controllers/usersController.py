# Handles user accounts and login logic.
# Validates usernames and passwords, hashes them, and stores account info.
# Keeps auth rules separate from Firestore access.

import hashlib
import hmac
import os
import re
from model import usersModel

USERNAME_RE = re.compile(r'^[a-z0-9_]{3,20}$')


# Password hashing follows a PBKDF2 workflow so stored credentials are not
# kept as plain text and can be compared safely during login.
# Hashes a password with a salt using PBKDF2.
def _hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200_000)


# Cleans and validates a username.
def parseUsername(text):
    name = text.strip().lower()
    if not USERNAME_RE.match(name):
        raise ValueError('use 3-20 lowercase letters, numbers or underscores.')
    return name


# Makes sure the password is long enough.
def parsePassword(text):
    if len(text) < 6:
        raise ValueError('the password must have at least 6 characters.')
    return text


# Checks whether a username is still available.
def isAvailable(username):
    return usersModel.getUser(parseUsername(username)) is None


# Registers a new user and stores the hash and salt.
def register(username, password):
    username = parseUsername(username)
    parsePassword(password)
    salt = os.urandom(16)
    created = usersModel.createUser(username, _hash(password, salt).hex(), salt.hex())
    if not created:
        raise ValueError('That username is already taken.')
    return username


# Validates login credentials and returns the username on success.
def login(username, password):
    generic = ValueError('Invalid username or password.')
    try:
        username = parseUsername(username)
    except ValueError:
        raise generic from None
    user = usersModel.getUser(username)
    if user is None:
        raise generic
    expected = user['passwordHash']
    actual = _hash(password, bytes.fromhex(user['salt'])).hex()
    if not hmac.compare_digest(actual, expected):
        raise generic
    return username