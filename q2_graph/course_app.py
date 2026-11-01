from course import CORE, ELECTIVE, Course
from graph import Graph

MENU = """
===== Course Prerequisites =====
  1. List all course names
  2. View full details of a course
  3. View prerequisites of a course
  4. View courses unlocked by a course
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


def ask_course(courses_by_code):
    """Ask for a course code and return that Course, or None if no course has that code.

    Codes are matched in upper case, so "cs201" finds CS201.
    """
    code = input("Course code: ").strip().upper()
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


def run_menu(graph, courses_by_code):
    """Show the menu and carry out the user's choices until they choose Exit."""
    while True:
        print(MENU)
        choice = input("Choose an option (0-4): ").strip()
        if choice == "1":
            list_course_names(graph)
        elif choice == "2":
            view_full_details(courses_by_code)
        elif choice == "3":
            view_prerequisites(graph, courses_by_code)
        elif choice == "4":
            view_unlocked(graph, courses_by_code)
        elif choice == "0":
            print("Goodbye.")
            return
        else:
            print("Please enter a number from 0 to 4.")


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
