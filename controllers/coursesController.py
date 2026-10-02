# Handles course logic.
# Checks user access, validates course fields, and prevents bad updates or deletes.

from model import coursesModel, assignmentModel

FIELDS = ('name', 'code', 'instructor', 'semester')


# Security check: a user may only act on courses that belong to their account.
# Confirms the course exists and belongs to the current user.
def requireCourse(user_id, course_id):
    course = coursesModel.getCourse(course_id)
    if course is None or course.get('userId') != user_id:
        raise ValueError('Course not found.')
    return course


# Adds a new course for the current user.
def addCourse(user_id, name, code, instructor, semester):
    values = [v.strip() for v in (name, code, instructor, semester)]
    if not all(values):
        raise ValueError('All course fields are required.')
    return coursesModel.addCourse(user_id, *values)


# Lists the user's courses sorted by course code.
def getCourses(user_id):
    return sorted(coursesModel.getCourses(user_id), key=lambda c: c['code'].lower())


# Updates allowed course fields while rejecting empty values.
def editCourse(user_id, course_id, changes):
    clean = {k: v.strip() for k, v in changes.items() if k in FIELDS and v is not None}
    if any(not v for v in clean.values()):
        raise ValueError('Course fields cannot be empty.')
    requireCourse(user_id, course_id)
    if clean:
        coursesModel.updateCourse(course_id, clean)


# Deletes a course and all of its assignments.
def deleteCourse(user_id, course_id):
    requireCourse(user_id, course_id)
    assignmentModel.deleteByCourse(user_id, course_id)
    coursesModel.deleteCourse(course_id)