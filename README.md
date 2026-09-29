# Overview

I built this project to get hands-on experience with cloud databases: designing data around the queries an app needs, handling user accounts, and keeping database code, business logic, and user interface separate. As a challenge, I used Firestore for everything, including authentication.

It is a command-line course and assignment tracker. Each user creates an account and manages their own courses and assignments, all stored in Google Firestore through the Firebase Admin SDK. Changes made in the app appear in the Firebase dashboard right away.

**How to use it**

1. Create a Firebase project, enable Firestore, and download a service account key (Project settings > Service accounts > Generate new private key).
2. Save the key as `model/dbKey.json` (do not commit it).
3. Run `pip install firebase-admin`, then `python app.py` from the project root.
4. Create an account or log in, then use the numbered menu to add, edit, and delete courses and assignments, update status and due dates, list a course's assignments, filter by status, and see what is due soon.
5. Invalid input re-asks the question. Type `back` or choose `0` to go back.

**Structure:** `app.py` (menu), `controllers/` (validation and logic), `model/` (Firestore access only).

A 4-5 minute video demonstration (software running, code walkthrough, and cloud database view) is available on request. Contact me at luisalejandro632@gmail.com.

# Cloud Database

I used **Google Cloud Firestore**, a serverless NoSQL document database. Data is stored as documents (sets of fields) inside collections, with no fixed schema.

- **users**: `username` (also the document ID), `passwordHash`, `salt`
- **courses**: `userId`, `name`, `code`, `instructor`, `semester`
- **assignments**: `userId`, `courseId`, `title`, `description`, `dueDate`, `points`, `status`

Assignments link to courses through `courseId`, and both link to their owner through `userId`. Passwords are stored as salted PBKDF2 hashes. Data separation between users is enforced in the app code, since the Admin SDK bypasses Firestore security rules.

# Development Environment

- Python 3.13, Visual Studio Code, Git and GitHub, Firebase Console
- Libraries: `firebase-admin` (includes `google-cloud-firestore`), plus the standard library (`datetime`, `hashlib`, `hmac`, `os`, `re`, `math`, `getpass`)

# Useful Websites

- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Firebase Admin SDK Setup](https://firebase.google.com/docs/admin/setup)
- [Firestore Python Client Reference](https://cloud.google.com/python/docs/reference/firestore/latest)
- [Firestore Quotas and Limits](https://firebase.google.com/docs/firestore/quotas)

# Future Work

- Switch sign-in to Firebase Authentication, with password reset
- Add Firestore security rules
- Build a graphical or web interface
