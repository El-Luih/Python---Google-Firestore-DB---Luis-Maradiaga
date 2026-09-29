import math
from datetime import datetime, timedelta
from model import assignmentModel
from controllers import coursesController

STATUSES = ['todo', 'in progress', 'done']


def parseDate(text):
    try:
        return datetime.strptime(text, '%Y-%m-%d').astimezone()
    except ValueError:
        raise ValueError('use the format YYYY-MM-DD (for example 2026-10-15).') from None


def parsePoints(text):
    try:
        points = float(text)
    except ValueError:
        raise ValueError('points must be a number.') from None
    if not math.isfinite(points) or points < 0:
        raise ValueError('points must be zero or more.')
    return points


def parseDays(text):
    if not text:
        return 7
    try:
        days = int(text)
    except ValueError:
        raise ValueError('enter a whole number of days.') from None
    if days < 1:
        raise ValueError('days must be at least 1.')
    return days


def _requireAssignment(user_id, assignment_id):
    a = assignmentModel.getAssignment(assignment_id)
    if a is None or a.get('userId') != user_id:
        raise ValueError('Assignment not found.')
    return a


def addAssignment(user_id, course_id, title, description, due_date, points):
    if not title.strip():
        raise ValueError('Title is required.')
    coursesController.requireCourse(user_id, course_id)
    return assignmentModel.addAssignment(user_id, course_id, title.strip(),
                                         description, due_date, points, STATUSES[0])


def editAssignment(user_id, assignment_id, changes):
    #changes may contain title, description, points. None means 'keep'.
    clean = {k: v for k, v in changes.items()
             if k in ('title', 'description', 'points') and v is not None}
    if 'title' in clean:
        clean['title'] = clean['title'].strip()
        if not clean['title']:
            raise ValueError('Title is required.')
    if 'points' in clean and (not math.isfinite(clean['points']) or clean['points'] < 0):
        raise ValueError('points must be zero or more.')
    _requireAssignment(user_id, assignment_id)
    if clean:
        assignmentModel.updateAssignment(assignment_id, clean)


def updateStatus(user_id, assignment_id, status):
    if status not in STATUSES:
        raise ValueError('Invalid status.')
    _requireAssignment(user_id, assignment_id)
    assignmentModel.updateAssignment(assignment_id, {'status': status})


def updateDueDate(user_id, assignment_id, due_date):
    _requireAssignment(user_id, assignment_id)
    assignmentModel.updateAssignment(assignment_id, {'dueDate': due_date})


def deleteAssignment(user_id, assignment_id):
    _requireAssignment(user_id, assignment_id)
    assignmentModel.deleteAssignment(assignment_id)


def getAssignmentsForCourse(user_id, course_id):
    items = assignmentModel.queryByCourse(user_id, course_id)
    return sorted(items, key=lambda a: a['dueDate'])


def getAssignmentsByStatus(user_id, status):
    items = assignmentModel.queryByStatus(user_id, status)
    return sorted(items, key=lambda a: a['dueDate'])


def getDueSoon(user_id, days=7):
    #Filtered in Python: equality on userId plus a range on dueDate would need a composite index.
    now = datetime.now().astimezone()
    end = now + timedelta(days=days)
    items = assignmentModel.queryByUser(user_id)
    soon = [a for a in items if now <= a['dueDate'] <= end and a['status'] != 'done']
    return sorted(soon, key=lambda a: a['dueDate'])