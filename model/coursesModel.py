# Firestore access for courses.
# Reads and writes course data without extra business logic.

from google.cloud.firestore_v1.base_query import FieldFilter
from model.dbAdminInitializer import firestoreDB

courses = firestoreDB.collection('courses')


# Adds the document ID to a Firestore course record.
def _with_id(doc):
    return {**doc.to_dict(), 'id': doc.id}


# Creates a new course document.
def addCourse(user_id, name, code, instructor, semester):
    _, ref = courses.add({
        'userId': user_id,
        'name': name,
        'code': code,
        'instructor': instructor,
        'semester': semester,
    })
    return ref.id


# Loads one course by document ID.
def getCourse(course_id):
    doc = courses.document(course_id).get()
    return _with_id(doc) if doc.exists else None


# Gets all courses for one user.
def getCourses(user_id):
    q = courses.where(filter=FieldFilter('userId', '==', user_id))
    return [_with_id(d) for d in q.stream()]


# Updates selected fields on a course.
def updateCourse(course_id, fields):
    courses.document(course_id).update(fields)


# Deletes one course document.
def deleteCourse(course_id):
    courses.document(course_id).delete()