from model import coursesModel, assignmentModel

FIELDS = ('name', 'code', 'instructor', 'semester')


def requireCourse(user_id, course_id):
    #Returns the course only if it belongs to this user.
    course = coursesModel.getCourse(course_id)
    if course is None or course.get('userId') != user_id:
        raise ValueError('Course not found.')
    return course


def addCourse(user_id, name, code, instructor, semester):
    values = [v.strip() for v in (name, code, instructor, semester)]
    if not all(values):
        raise ValueError('All course fields are required.')
    return coursesModel.addCourse(user_id, *values)


def getCourses(user_id):
    return sorted(coursesModel.getCourses(user_id), key=lambda c: c['code'].lower())


def editCourse(user_id, course_id, changes):
    #changes: {field: new value}. A value of None means 'keep the current one'.
    clean = {k: v.strip() for k, v in changes.items() if k in FIELDS and v is not None}
    if any(not v for v in clean.values()):
        raise ValueError('Course fields cannot be empty.')
    requireCourse(user_id, course_id)
    if clean:
        coursesModel.updateCourse(course_id, clean)


def deleteCourse(user_id, course_id):
    #Deletes the course's assignments first, then the course itself.
    requireCourse(user_id, course_id)
    assignmentModel.deleteByCourse(user_id, course_id)
    coursesModel.deleteCourse(course_id)