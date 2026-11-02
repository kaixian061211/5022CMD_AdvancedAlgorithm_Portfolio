CORE = "core"
ELECTIVE = "elective"
LEVELS = (CORE, ELECTIVE)


class Course:
    """A course in the programme, used as a vertex in the prerequisite graph.

    Attribute types:
      code (str):         an identifier such as "CS201", made of letters and digits.
      name (str):         free text.
      credit_hours (int): credits are always whole numbers.
      level (str):        CORE or ELECTIVE. Kept as readable text, and the
                          constructor rejects any other value.
      description (str):  free text.

    Two Course objects are equal when their codes match, and the hash uses
    the code too, so the graph and dict lookups treat them as one course.
    """

    def __init__(self, code, name, credit_hours, level, description):
        """Create a course from already-validated values."""
        if level not in LEVELS:
            raise ValueError(f"level must be one of {LEVELS}, not {level!r}")
        self.code = code
        self.name = name
        self.credit_hours = credit_hours
        self.level = level
        self.description = description

    def __eq__(self, other):
        """Return True if other is a Course with the same code."""
        return isinstance(other, Course) and self.code == other.code

    def __hash__(self):
        """Hash on the code, so courses that are equal also have equal hashes."""
        return hash(self.code)

    def __lt__(self, other):
        """Order courses by code, so sorted() lists them the same way every run."""
        return self.code < other.code

    def __repr__(self):
        """Return a short form such as Course('CS201'), used in error messages."""
        return f"Course({self.code!r})"

    def details(self):
        """Return every field as (label, text) pairs, in display order."""
        return [
            ("Code", self.code),
            ("Name", self.name),
            ("Credit hours", str(self.credit_hours)),
            ("Level", self.level.capitalize()),
            ("Description", self.description),
        ]

    def profile(self):
        """Return the fields shown in a profile: all of them for a core course,
        only the name for an elective."""
        if self.level == CORE:
            return self.details()
        return [("Name", self.name)]
