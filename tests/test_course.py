import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "q2_graph"))

from course import CORE, ELECTIVE, Course


def make_course(code, name="Some course", level=CORE):
    """Return a Course with default values for the fields a test does not care about."""
    return Course(code, name, 3, level, "A description.")


class TestCourseIdentity(unittest.TestCase):
    """Courses are equal, hashed and ordered by their code."""

    def test_equal_when_codes_match(self):
        """Two objects with the same code are equal even if other fields differ."""
        self.assertEqual(make_course("CS201", "Data Structures"),
                         make_course("CS201", "Another name"))

    def test_not_equal_when_codes_differ(self):
        """Different codes mean different courses."""
        self.assertNotEqual(make_course("CS201"), make_course("CS202"))

    def test_not_equal_to_other_types(self):
        """A course is not equal to its code as a plain string."""
        self.assertNotEqual(make_course("CS201"), "CS201")

    def test_equal_courses_have_equal_hashes(self):
        """Equal courses hash the same, so a set keeps only one of them."""
        first = make_course("CS201")
        second = make_course("CS201", "Another name")
        self.assertEqual(hash(first), hash(second))
        self.assertEqual(len({first, second}), 1)

    def test_sorted_by_code(self):
        """sorted() orders courses by code."""
        courses = [make_course("MA101"), make_course("CS301"), make_course("CS101")]
        codes = []
        for course in sorted(courses):
            codes.append(course.code)
        self.assertEqual(codes, ["CS101", "CS301", "MA101"])

    def test_repr(self):
        """repr shows the code, which makes error messages readable."""
        self.assertEqual(repr(make_course("CS201")), "Course('CS201')")


class TestCourseFields(unittest.TestCase):
    """Field validation and the details list."""

    def test_invalid_level(self):
        """Only core and elective are accepted."""
        with self.assertRaises(ValueError):
            make_course("CS201", level="optional")

    def test_details(self):
        """Every field is listed, with the level capitalised."""
        course = Course("CS302", "Web Development", 3, ELECTIVE, "Web apps.")
        self.assertEqual(course.details(), [
            ("Code", "CS302"),
            ("Name", "Web Development"),
            ("Credit hours", "3"),
            ("Level", "Elective"),
            ("Description", "Web apps."),
        ])


if __name__ == "__main__":
    unittest.main()
