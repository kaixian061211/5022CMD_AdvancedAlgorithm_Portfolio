from course import CORE, ELECTIVE, Course
from graph import Graph

MAX_CODE_LENGTH = 10
MAX_NAME_LENGTH = 40
MAX_DESCRIPTION_LENGTH = 100
MAX_CREDIT_HOURS = 20

CODE_ERROR = f"Use 1 to {MAX_CODE_LENGTH} letters or digits, e.g. CS305."
NAME_ERROR = f"Enter 1 to {MAX_NAME_LENGTH} characters."
DESCRIPTION_ERROR = f"Enter 1 to {MAX_DESCRIPTION_LENGTH} characters."
CREDIT_ERROR = f"Enter a whole number from 1 to {MAX_CREDIT_HOURS}."
LEVEL_ERROR = "Enter core or elective (or c / e)."

MENU = """
===== Course Prerequisites =====
  1. List all course names
  2. View full details of a course
  3. View prerequisites of a course
  4. View courses unlocked by a course
  5. Add a course
  6. View course profile
  7. Add a prerequisite
  8. Remove a prerequisite
  0. Exit"""

# Each pair is (prerequisite code, code of the course it unlocks), which is
# also the direction of the edge in the graph.
SAMPLE_PREREQUISITES = [
    ("CS101", "CS102"),
    ("CS102", "CS201"),
    ("MA101", "CS201"),
    ("CS102", "CS202"),
    ("MA101", "MA201"),
    ("CS201", "CS301"),
    ("MA101", "CS301"),
    ("CS202", "CS302"),
    ("CS301", "CS303"),
    ("MA201", "CS303"),
    ("CS102", "CS304"),
]


def sample_courses():
    """Return the courses the programme starts with."""
    return [
        Course("CS101", "Programming Fundamentals", 4, CORE,
               "Variables, control flow, functions and problem solving in Python."),
        Course("MA101", "Discrete Mathematics", 3, CORE,
               "Logic, sets, relations, proof techniques and graph basics."),
        Course("CS102", "Object-Oriented Programming", 4, CORE,
               "Classes, inheritance, polymorphism and unit testing."),
        Course("MA201", "Probability and Statistics", 3, CORE,
               "Probability, distributions, sampling and hypothesis tests."),
        Course("CS201", "Data Structures", 4, CORE,
               "Lists, stacks, queues, trees, hash tables and their costs."),
        Course("CS202", "Database Systems", 3, CORE,
               "Relational design, SQL, normalisation and transactions."),
        Course("CS301", "Advanced Algorithms", 4, CORE,
               "Graph algorithms, complexity analysis and concurrency."),
        Course("CS302", "Web Development", 3, ELECTIVE,
               "Building database-backed web applications."),
        Course("CS303", "Machine Learning", 3, ELECTIVE,
               "Regression, classification and model evaluation."),
        Course("CS304", "Mobile App Development", 3, ELECTIVE,
               "Designing and building apps for mobile devices."),
    ]


def add_course(graph, courses_by_code, course):
    """Add a course as a graph vertex and to the code lookup.

    Every course is added through here, so the graph and the lookup always
    hold the same courses.
    """
    graph.addVertex(course)
    courses_by_code[course.code] = course


def build_catalogue():
    """Return a graph of the sample courses and their code -> Course lookup."""
    graph = Graph()
    courses_by_code = {}
    for course in sample_courses():
        add_course(graph, courses_by_code, course)
    for prerequisite_code, course_code in SAMPLE_PREREQUISITES:
        graph.addEdge(courses_by_code[prerequisite_code], courses_by_code[course_code])
    return graph, courses_by_code


def parse_code(text):
    """Return text as an upper-case course code, or None if it is not 1-10 letters or digits."""
    text = text.upper()
    if 1 <= len(text) <= MAX_CODE_LENGTH and text.isalnum():
        return text
    return None


def parse_name(text):
    """Return text if it has 1 to MAX_NAME_LENGTH characters, otherwise None."""
    if 1 <= len(text) <= MAX_NAME_LENGTH:
        return text
    return None


def parse_description(text):
    """Return text if it has 1 to MAX_DESCRIPTION_LENGTH characters, otherwise None."""
    if 1 <= len(text) <= MAX_DESCRIPTION_LENGTH:
        return text
    return None


def parse_credit_hours(text):
    """Return text as an int from 1 to MAX_CREDIT_HOURS, or None if invalid."""
    try:
        credit_hours = int(text)
    except ValueError:
        return None
    if credit_hours < 1 or credit_hours > MAX_CREDIT_HOURS:
        return None
    return credit_hours


def parse_level(text):
    """Return CORE for core/c, ELECTIVE for elective/e, and None for anything else."""
    text = text.lower()
    if text == "core" or text == "c":
        return CORE
    if text == "elective" or text == "e":
        return ELECTIVE
    return None


def read_value(prompt, parse, error):
    """Ask until parse() accepts the answer, then return the parsed value.

    parse is one of the parse_ functions: it returns the value, or None if
    the text is invalid, in which case the error is shown and the question repeated.
    """
    while True:
        value = parse(input(f"{prompt}: ").strip())
        if value is not None:
            return value
        print(f"  {error}")


def ask_course(courses_by_code, prompt="Course code"):
    """Ask for a course code and return that Course, or None if no course has that code.

    Codes are matched in upper case, so "cs201" finds CS201.
    """
    code = input(f"{prompt}: ").strip().upper()
    if code == "":
        print("No course code entered.")
        return None
    course = courses_by_code.get(code)
    if course is None:
        print(f"No course with code '{code}'. Option 1 lists all courses.")
    return course


def print_course_list(courses):
    """Print courses sorted by code, one per line, or (none) for an empty list.

    The graph keeps neighbours in sets, which have no fixed order, so sorting
    here makes the output the same on every run.
    """
    if len(courses) == 0:
        print("  (none)")
        return
    for course in sorted(courses):
        print(f"  {course.code:<8}{course.name}")


def list_course_names(graph):
    """Print the code and name of every course, sorted by code."""
    courses = graph.listVertices()
    print(f"All courses ({len(courses)}):")
    print_course_list(courses)


def view_full_details(courses_by_code):
    """Print every field of one course, whatever its level."""
    course = ask_course(courses_by_code)
    if course is None:
        return
    for label, value in course.details():
        print(f"  {label:<14}{value}")


def view_prerequisites(graph, courses_by_code):
    """Print the courses that must be taken before the chosen course (its incoming edges)."""
    course = ask_course(courses_by_code)
    if course is None:
        return
    print(f"Prerequisites of {course.code} {course.name}:")
    print_course_list(graph.listIncomingAdjacentVertex(course))


def view_unlocked(graph, courses_by_code):
    """Print the courses the chosen course is a prerequisite for (its outgoing edges)."""
    course = ask_course(courses_by_code)
    if course is None:
        return
    print(f"Courses unlocked by {course.code} {course.name}:")
    print_course_list(graph.listOutgoingAdjacentVertex(course))


def add_new_course(graph, courses_by_code):
    """Ask for a new course's details and add it to the graph and the lookup."""
    code = read_value("New course code", parse_code, CODE_ERROR)
    if code in courses_by_code:
        print(f"A course with code {code} already exists.")
        return
    name = read_value("Name", parse_name, NAME_ERROR)
    credit_hours = read_value("Credit hours", parse_credit_hours, CREDIT_ERROR)
    level = read_value("Level (core/elective)", parse_level, LEVEL_ERROR)
    description = read_value("Description", parse_description, DESCRIPTION_ERROR)
    add_course(graph, courses_by_code, Course(code, name, credit_hours, level, description))
    print(f"Added {code} {name}. Use option 7 to give it prerequisites.")


def view_profile(courses_by_code):
    """Print a course's profile: every field for a core course, only the name for an elective."""
    course = ask_course(courses_by_code)
    if course is None:
        return
    print("Course profile:")
    for label, value in course.profile():
        print(f"  {label:<14}{value}")


def check_new_prerequisite(graph, prerequisite, course):
    """Return why prerequisite cannot be added to course, or None if it can.

    The new edge would be prerequisite -> course. If course can already reach
    prerequisite, that path plus the new edge would form a cycle, so each
    course would end up needing the other before it.
    """
    if prerequisite == course:
        return "A course cannot be its own prerequisite."
    if graph.hasEdge(prerequisite, course):
        return f"{prerequisite.code} is already a prerequisite of {course.code}."
    if graph.hasPath(course, prerequisite):
        return (f"{course.code} already leads to {prerequisite.code}, so making "
                f"{prerequisite.code} a prerequisite of {course.code} would create a cycle.")
    return None


def add_prerequisite(graph, courses_by_code):
    """Ask for a course and a prerequisite, and add the edge if it passes every check."""
    course = ask_course(courses_by_code, "Course that needs the prerequisite")
    if course is None:
        return
    prerequisite = ask_course(courses_by_code, "Prerequisite course code")
    if prerequisite is None:
        return
    problem = check_new_prerequisite(graph, prerequisite, course)
    if problem is not None:
        print(f"Not added. {problem}")
        return
    graph.addEdge(prerequisite, course)
    print(f"{prerequisite.code} is now a prerequisite of {course.code}.")


def remove_prerequisite(graph, courses_by_code):
    """Show a course's prerequisites, ask which one to remove, and remove that edge."""
    course = ask_course(courses_by_code, "Course to remove a prerequisite from")
    if course is None:
        return
    current = graph.listIncomingAdjacentVertex(course)
    if len(current) == 0:
        print(f"{course.code} has no prerequisites.")
        return
    print(f"Current prerequisites of {course.code}:")
    print_course_list(current)
    prerequisite = ask_course(courses_by_code, "Prerequisite to remove")
    if prerequisite is None:
        return
    if graph.removeEdge(prerequisite, course):
        print(f"{prerequisite.code} is no longer a prerequisite of {course.code}.")
    else:
        print(f"{prerequisite.code} is not a prerequisite of {course.code}.")


def run_menu(graph, courses_by_code):
    """Show the menu and carry out the user's choices until they choose Exit."""
    while True:
        print(MENU)
        choice = input("Choose an option (0-8): ").strip()
        if choice == "1":
            list_course_names(graph)
        elif choice == "2":
            view_full_details(courses_by_code)
        elif choice == "3":
            view_prerequisites(graph, courses_by_code)
        elif choice == "4":
            view_unlocked(graph, courses_by_code)
        elif choice == "5":
            add_new_course(graph, courses_by_code)
        elif choice == "6":
            view_profile(courses_by_code)
        elif choice == "7":
            add_prerequisite(graph, courses_by_code)
        elif choice == "8":
            remove_prerequisite(graph, courses_by_code)
        elif choice == "0":
            print("Goodbye.")
            return
        else:
            print("Please enter a number from 0 to 8.")


def main():
    """Load the sample courses and run the menu."""
    graph, courses_by_code = build_catalogue()
    try:
        run_menu(graph, courses_by_code)
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C or end of input: leave cleanly instead of showing a traceback.
        print("\nExiting.")


if __name__ == "__main__":
    main()
