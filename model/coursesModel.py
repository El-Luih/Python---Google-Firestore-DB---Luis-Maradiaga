from google.cloud.firestore_v1.base_query import FieldFilter
from model.dbAdminInitializer import firestoreDB

courses = firestoreDB.collection('courses')


def _with_id(doc):
    return {**doc.to_dict(), 'id': doc.id}


def addCourse(user_id, name, code, instructor, semester):
    _, ref = courses.add({
        'userId': user_id,
        'name': name,
        'code': code,
        'instructor': instructor,
        'semester': semester,
    })
    return ref.id


def getCourse(course_id):
    doc = courses.document(course_id).get()
    return _with_id(doc) if doc.exists else None


def getCourses(user_id):
    q = courses.where(filter=FieldFilter('userId', '==', user_id))
    return [_with_id(d) for d in q.stream()]


def updateCourse(course_id, fields):
    #update() changes only the fields passed in and leaves the rest alone.
    courses.document(course_id).update(fields)


def deleteCourse(course_id):
    courses.document(course_id).delete()