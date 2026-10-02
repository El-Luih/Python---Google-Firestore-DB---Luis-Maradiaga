# Firestore access for assignments.
# Creates, updates, deletes, and queries assignment data.

from google.cloud.firestore_v1.base_query import FieldFilter
from model.dbAdminInitializer import firestoreDB

# Firestore collection name matches the app's conceptual data model.
assignments = firestoreDB.collection('assignments')


# Adds the document ID to a Firestore record dictionary.
def _with_id(doc):
    return {**doc.to_dict(), 'id': doc.id}


# Filters assignments to the current user only.
def _mine(user_id):
    return assignments.where(filter=FieldFilter('userId', '==', user_id))


# Creates a new assignment record.
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


# Loads one assignment by document ID.
def getAssignment(assignment_id):
    doc = assignments.document(assignment_id).get()
    return _with_id(doc) if doc.exists else None


# Updates selected fields on an assignment.
def updateAssignment(assignment_id, fields):
    assignments.document(assignment_id).update(fields)


# Deletes one assignment.
def deleteAssignment(assignment_id):
    assignments.document(assignment_id).delete()


# Deletes all assignments for one course in batches.
def deleteByCourse(user_id, course_id):
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


# Gets all assignments in one course.
def queryByCourse(user_id, course_id):
    q = _mine(user_id).where(filter=FieldFilter('courseId', '==', course_id))
    return [_with_id(d) for d in q.stream()]


# Gets all assignments matching a status.
def queryByStatus(user_id, status):
    q = _mine(user_id).where(filter=FieldFilter('status', '==', status))
    return [_with_id(d) for d in q.stream()]


# Gets every assignment for the current user.
def queryByUser(user_id):
    return [_with_id(d) for d in _mine(user_id).stream()]