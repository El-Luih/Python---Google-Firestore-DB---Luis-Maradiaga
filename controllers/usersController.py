import hashlib
import hmac
import os
import re
from model import usersModel

USERNAME_RE = re.compile(r'^[a-z0-9_]{3,20}$')


def _hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 200_000)


def parseUsername(text):
    name = text.strip().lower()
    if not USERNAME_RE.match(name):
        raise ValueError('use 3-20 lowercase letters, numbers or underscores.')
    return name


def parsePassword(text):
    if len(text) < 6:
        raise ValueError('the password must have at least 6 characters.')
    return text


def isAvailable(username):
    return usersModel.getUser(parseUsername(username)) is None


def register(username, password):
    username = parseUsername(username)
    parsePassword(password)
    salt = os.urandom(16)
    created = usersModel.createUser(username, _hash(password, salt).hex(), salt.hex())
    if not created:
        raise ValueError('That username is already taken.')
    return username


def login(username, password):
    #Returns the username (used as the user ID) or raises ValueError.
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