from google.cloud.firestore_v1.base_query import FieldFilter
from model.dbAdminInitializer import firestoreDB

assignments = firestoreDB.collection('assignments')


def _with_id(doc):
    return {**doc.to_dict(), 'id': doc.id}


def _mine(user_id):
    return assignments.where(filter=FieldFilter('userId', '==', user_id))


def addAssignment(user_id, course_id, title, description, due_date, points, status):
    _, ref = assignments.add({
        'userId': user_id,
        'courseId': course_id,
        'title': title,
        'description': description,
        'dueDate': due_date,
        'points': points,
        'status': status,
    })
    return ref.id


def getAssignment(assignment_id):
    doc = assignments.document(assignment_id).get()
    return _with_id(doc) if doc.exists else None


def updateAssignment(assignment_id, fields):
    assignments.document(assignment_id).update(fields)


def deleteAssignment(assignment_id):
    assignments.document(assignment_id).delete()


def deleteByCourse(user_id, course_id):
    #Deletes every assignment of a course in batches (limit is 500 writes).
    q = _mine(user_id).where(filter=FieldFilter('courseId', '==', course_id))
    batch = firestoreDB.batch()
    count = 0
    for doc in q.stream():
        batch.delete(doc.reference)
        count += 1
        if count % 400 == 0:
            batch.commit()
            batch = firestoreDB.batch()
    batch.commit()


def queryByCourse(user_id, course_id):
    q = _mine(user_id).where(filter=FieldFilter('courseId', '==', course_id))
    return [_with_id(d) for d in q.stream()]


def queryByStatus(user_id, status):
    q = _mine(user_id).where(filter=FieldFilter('status', '==', status))
    return [_with_id(d) for d in q.stream()]


def queryByUser(user_id):
    return [_with_id(d) for d in _mine(user_id).stream()]