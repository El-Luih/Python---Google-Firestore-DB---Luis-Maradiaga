from getpass import getpass
from controllers import usersController, coursesController, assignmentController
from controllers.validators import required


class GoBack(Exception):
    #Raised by any prompt when the user types 'back' or chooses 0.
    pass

# ---------- input helpers ----------
def ask(prompt):
    value = input(f'{prompt} (or "back"): ').strip()
    if value.lower() == 'back':
        raise GoBack
    return value


def askPassword(prompt):
    value = input(f'{prompt} (or "back"): ')
    if value.strip().lower() == 'back':
        raise GoBack
    return value


def askValid(prompt, parse):
    #Keeps asking the same question until parse() accepts the answer.
    while True:
        try:
            return parse(ask(prompt))
        except ValueError as e:
            print(f'  Invalid input: {e}')


def askKeep(label, current, parse=str):
    #Edit prompt: pressing Enter keeps the current value (returns None).
    while True:
        text = ask(f'{label} [{current}] - Enter to keep')
        if not text:
            return None
        try:
            return parse(text)
        except ValueError as e:
            print(f'  Invalid input: {e}')


def parseYesNo(text):
    answer = text.lower()
    if answer not in ('y', 'n'):
        raise ValueError('answer y or n.')
    return answer == 'y'


def chooseIndex(count, prompt):
    def parse(text):
        if not text.isdigit() or not 0 <= int(text) <= count:
            raise ValueError(f'enter a number from 0 to {count}.')
        return int(text)

    n = askValid(prompt, parse)
    if n == 0:
        raise GoBack
    return n - 1


# ---------- pickers ----------
def describe(a):
    return f"{a['title']} ({a['status']}, {a['points']:g} pts, due {a['dueDate']:%Y-%m-%d})"


def pickCourse(user):
    courses = coursesController.getCourses(user)
    if not courses:
        print('You have no courses yet.')
        raise GoBack
    for i, c in enumerate(courses, 1):
        print(f"{i}. {c['code']} - {c['name']}")
    print('0. Back')
    return courses[chooseIndex(len(courses), 'Course number')]


def pickAssignment(user, course):
    items = assignmentController.getAssignmentsForCourse(user, course['id'])
    if not items:
        print('No assignments for this course.')
        raise GoBack
    for i, a in enumerate(items, 1):
        print(f'{i}. {describe(a)}')
    print('0. Back')
    return items[chooseIndex(len(items), 'Assignment number')]


def pickCourseAndAssignment(user):
    #Back from the assignment list returns to the course list.
    while True:
        course = pickCourse(user)
        try:
            return pickAssignment(user, course)
        except GoBack:
            continue


def readDate():
    return askValid('Due date (YYYY-MM-DD)', assignmentController.parseDate)


def readPoints():
    return askValid('Points', assignmentController.parsePoints)


def readStatus():
    statuses = assignmentController.STATUSES
    for i, s in enumerate(statuses, 1):
        print(f'{i}. {s}')
    print('0. Back')
    return statuses[chooseIndex(len(statuses), 'Status')]


def printAssignments(items, emptyMessage='Nothing found.'):
    print()
    if not items:
        print(emptyMessage)
    for a in items:
        print(f'- {describe(a)}')
    input('\nPress Enter to go back to the menu...')


# ---------- accounts ----------
AUTH_MENU = """
=== Course & Assignment Tracker ===
1. Log in
2. Create account
0. Quit
"""


def loginFlow():
    while True:
        username = ask('Username')
        password = askPassword('Password')
        try:
            return usersController.login(username, password)
        except ValueError as e:
            print(f'  {e}')


def registerFlow():
    while True:
        username = askValid('Choose a username (3-20 letters, numbers or _)',
                            usersController.parseUsername)
        if usersController.isAvailable(username):
            break
        print('  That username is already taken.')
    while True:
        password = askPassword('Choose a password (min 6 characters)')
        try:
            usersController.parsePassword(password)
        except ValueError as e:
            print(f'  Invalid input: {e}')
            continue
        if askPassword('Confirm password') == password:
            break
        print('  Passwords do not match.')
    return usersController.register(username, password)


def authScreen():
    #Returns the logged-in username, or None if the user quits.
    while True:
        print(AUTH_MENU)
        choice = input('> ').strip()
        try:
            if choice == '1':
                return loginFlow()
            if choice == '2':
                user = registerFlow()
                print('Account created.')
                return user
            if choice == '0':
                return None
            print('Choose a number from the menu.')
        except GoBack:
            print('Going back.')
        except ValueError as e:
            print(f'  {e}')
        except Exception as e:
            print(f'Something went wrong: {e}')


# ---------- main menu ----------
MENU = """
1. Add course
2. Edit course
3. Add assignment
4. Edit assignment (title, description, points)
5. Update assignment status
6. Update assignment due date
7. Delete assignment
8. Delete course (and its assignments)
9. List everything for a course
10. Filter assignments by status
11. Show what's due soon
12. Log out
0. Quit
"""


def runSession(user):
    #Returns True to log out, False to quit the program.
    while True:
        print(MENU)
        choice = input('> ').strip()
        try:
            if choice == '1':
                coursesController.addCourse(
                    user,
                    askValid('Name', required('Name')),
                    askValid('Code', required('Code')),
                    askValid('Instructor', required('Instructor')),
                    askValid('Semester', required('Semester')))
                print('Course added.')
            elif choice == '2':
                course = pickCourse(user)
                changes = {
                    'name': askKeep('Name', course['name'], required('Name')),
                    'code': askKeep('Code', course['code'], required('Code')),
                    'instructor': askKeep('Instructor', course['instructor'], required('Instructor')),
                    'semester': askKeep('Semester', course['semester'], required('Semester')),
                }
                coursesController.editCourse(user, course['id'], changes)
                print('Course updated.')
            elif choice == '3':
                course = pickCourse(user)
                assignmentController.addAssignment(
                    user, course['id'],
                    askValid('Title', required('Title')),
                    ask('Description'),
                    readDate(),
                    readPoints())
                print('Assignment added.')
            elif choice == '4':
                a = pickCourseAndAssignment(user)
                changes = {
                    'title': askKeep('Title', a['title'], required('Title')),
                    'description': askKeep('Description', a['description']),
                    'points': askKeep('Points', f"{a['points']:g}", assignmentController.parsePoints),
                }
                assignmentController.editAssignment(user, a['id'], changes)
                print('Assignment updated.')
            elif choice == '5':
                a = pickCourseAndAssignment(user)
                assignmentController.updateStatus(user, a['id'], readStatus())
                print('Status updated.')
            elif choice == '6':
                a = pickCourseAndAssignment(user)
                assignmentController.updateDueDate(user, a['id'], readDate())
                print('Due date updated.')
            elif choice == '7':
                a = pickCourseAndAssignment(user)
                assignmentController.deleteAssignment(user, a['id'])
                print('Assignment deleted.')
            elif choice == '8':
                course = pickCourse(user)
                if askValid(f"Delete '{course['name']}' and all its assignments? (y/n)", parseYesNo):
                    coursesController.deleteCourse(user, course['id'])
                    print('Course deleted.')
                else:
                    print('Cancelled.')
            elif choice == '9':
                course = pickCourse(user)
                printAssignments(assignmentController.getAssignmentsForCourse(user, course['id']),
                                 'This course has no assignments yet.')
            elif choice == '10':
                status = readStatus()
                printAssignments(assignmentController.getAssignmentsByStatus(user, status),
                                 f"No assignments with status '{status}'.")
            elif choice == '11':
                days = askValid('Within how many days? (Enter for 7)', assignmentController.parseDays)
                printAssignments(assignmentController.getDueSoon(user, days),
                                 f'Nothing due in the next {days} days.')
            elif choice == '12':
                return True
            elif choice == '0':
                return False
            else:
                print('Choose a number from the menu.')
        except GoBack:
            print('Going back to the menu.')
        except ValueError as e:
            print(f'  {e}')
        except Exception as e:
            print(f'Something went wrong: {e}')


def main():
    while True:
        user = authScreen()
        if user is None:
            break
        print(f'\nWelcome, {user}!')
        if not runSession(user):
            break
    print('Goodbye!')


if __name__ == '__main__':
    main()