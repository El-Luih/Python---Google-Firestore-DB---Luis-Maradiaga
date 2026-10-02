# Course and assignment tracker CLI.
# Handles menu flow, login/signup, and input prompts.
# Sends user actions to controller functions without touching Firestore directly.

from getpass import getpass
from controllers import usersController, coursesController, assignmentController
from controllers.validators import required


class GoBack(Exception):
    # Raised when the user cancels a nested prompt by typing 'back' or selecting 0.
    pass

# ---------- Input helpers ----------
# These helpers keep the CLI consistent: they capture text, support a shared
# "back" escape path, and repeatedly ask until the user provides valid input.
# Prompts the user for text and cancels on back.
def ask(prompt):
    value = input(f'{prompt} (or "back"): ').strip()
    if value.lower() == 'back':
        raise GoBack
    return value


# Prompts for a password and cancels on back.
def askPassword(prompt):
    value = input(f'{prompt} (or "back"): ')
    if value.strip().lower() == 'back':
        raise GoBack
    return value


# Keeps asking until the answer passes validation.
def askValid(prompt, parse):
    while True:
        try:
            return parse(ask(prompt))
        except ValueError as e:
            print(f'  Invalid input: {e}')


# Lets the user keep the current value by pressing Enter.
def askKeep(label, current, parse=str):
    while True:
        text = ask(f'{label} [{current}] - Enter to keep')
        if not text:
            return None
        try:
            return parse(text)
        except ValueError as e:
            print(f'  Invalid input: {e}')


# Converts y/n input to a boolean.
def parseYesNo(text):
    answer = text.lower()
    if answer not in ('y', 'n'):
        raise ValueError('answer y or n.')
    return answer == 'y'


# Picks a numbered item from a list, with 0 for back.
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
# Formats an assignment for display in the menu.
def describe(a):
    return f"{a['title']} ({a['status']}, {a['points']:g} pts, due {a['dueDate']:%Y-%m-%d})"


# Lists the user's courses and lets them choose one.
def pickCourse(user):
    courses = coursesController.getCourses(user)
    if not courses:
        print('You have no courses yet.')
        raise GoBack
    for i, c in enumerate(courses, 1):
        print(f"{i}. {c['code']} - {c['name']}")
    print('0. Back')
    return courses[chooseIndex(len(courses), 'Course number')]


# Lists assignments for a course and lets the user choose one.
def pickAssignment(user, course):
    items = assignmentController.getAssignmentsForCourse(user, course['id'])
    if not items:
        print('No assignments for this course.')
        raise GoBack
    for i, a in enumerate(items, 1):
        print(f'{i}. {describe(a)}')
    print('0. Back')
    return items[chooseIndex(len(items), 'Assignment number')]


# Keeps selecting a course and assignment until the user picks one or backs out.
def pickCourseAndAssignment(user):
    while True:
        course = pickCourse(user)
        try:
            return pickAssignment(user, course)
        except GoBack:
            continue


# Reads a due date using the assignment date validator.
def readDate():
    return askValid('Due date (YYYY-MM-DD)', assignmentController.parseDate)


# Reads and validates a points value.
def readPoints():
    return askValid('Points', assignmentController.parsePoints)


# Shows assignment statuses and lets the user pick one.
def readStatus():
    statuses = assignmentController.STATUSES
    for i, s in enumerate(statuses, 1):
        print(f'{i}. {s}')
    print('0. Back')
    return statuses[chooseIndex(len(statuses), 'Status')]


# Prints a list of assignments with a simple return message.
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


# Runs the login flow until the user enters valid credentials.
def loginFlow():
    while True:
        username = ask('Username')
        password = askPassword('Password')
        try:
            return usersController.login(username, password)
        except ValueError as e:
            print(f'  {e}')


# Creates a new account after checking username and password rules.
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


# Shows the auth menu and returns the logged-in user or None to quit.
def authScreen():
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


# Runs the logged-in user's main menu until they log out or quit.
def runSession(user):
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


# Starts the app and loops through login/logout sessions.
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