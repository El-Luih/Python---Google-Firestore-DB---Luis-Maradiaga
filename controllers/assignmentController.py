# Handles assignment logic.
# Validates inputs and only lets a user work with their own assignments.

import math
from datetime import datetime, timedelta
from model import assignmentModel
from controllers import coursesController

# Supported workflow states for assignments. The app uses these strings to keep
# status filters and user prompts consistent across the interface.
STATUSES = ['todo', 'in progress', 'done']


# Parses a date string into a datetime object.
def parseDate(text):
    try:
        return datetime.strptime(text, '%Y-%m-%d').astimezone()
    except ValueError:
        raise ValueError('use the format YYYY-MM-DD (for example 2026-10-15).') from None


# Parses a numeric points value and rejects negatives.
def parsePoints(text):
    try:
        points = float(text)
    except ValueError:
        raise ValueError('points must be a number.') from None
    if not math.isfinite(points) or points < 0:
        raise ValueError('points must be zero or more.')
    return points


# Parses the number of days for the due-soon filter.
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


# Confirms an assignment exists and belongs to the current user.
def _requireAssignment(user_id, assignment_id):
    a = assignmentModel.getAssignment(assignment_id)
    if a is None or a.get('userId') != user_id:
        raise ValueError('Assignment not found.')
    return a


# Adds a new assignment to a course.
def addAssignment(user_id, course_id, title, description, due_date, points):
    if not title.strip():
        raise ValueError('Title is required.')
    coursesController.requireCourse(user_id, course_id)
    return assignmentModel.addAssignment(user_id, course_id, title.strip(),
                                         description, due_date, points, STATUSES[0])


# Updates allowed assignment fields and rejects invalid values.
def editAssignment(user_id, assignment_id, changes):
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


# Updates the assignment status for the current user.
def updateStatus(user_id, assignment_id, status):
    if status not in STATUSES:
        raise ValueError('Invalid status.')
    _requireAssignment(user_id, assignment_id)
    assignmentModel.updateAssignment(assignment_id, {'status': status})


# Updates the due date for an existing assignment.
def updateDueDate(user_id, assignment_id, due_date):
    _requireAssignment(user_id, assignment_id)
    assignmentModel.updateAssignment(assignment_id, {'dueDate': due_date})


# Deletes an assignment owned by the current user.
def deleteAssignment(user_id, assignment_id):
    _requireAssignment(user_id, assignment_id)
    assignmentModel.deleteAssignment(assignment_id)


# Gets all assignments for one course sorted by date.
def getAssignmentsForCourse(user_id, course_id):
    items = assignmentModel.queryByCourse(user_id, course_id)
    return sorted(items, key=lambda a: a['dueDate'])


# Filters assignments by status for the current user.
def getAssignmentsByStatus(user_id, status):
    items = assignmentModel.queryByStatus(user_id, status)
    return sorted(items, key=lambda a: a['dueDate'])


# Finds assignments due within the next number of days.
def getDueSoon(user_id, days=7):
    now = datetime.now().astimezone()
    end = now + timedelta(days=days)
    items = assignmentModel.queryByUser(user_id)
    soon = [a for a in items if now <= a['dueDate'] <= end and a['status'] != 'done']
    return sorted(soon, key=lambda a: a['dueDate'])