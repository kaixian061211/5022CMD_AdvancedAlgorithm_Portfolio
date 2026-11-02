import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

# The programs run as plain scripts from their own folders, so the tests
# put that folder on the import path in the same way.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "q2_graph"))

from course import CORE, ELECTIVE
from course_app import (SAMPLE_PREREQUISITES, add_new_course, add_prerequisite,
                        ask_course, build_catalogue, check_new_prerequisite,
                        parse_code, parse_credit_hours, parse_level,
                        parse_name, print_course_list, read_value,
                        remove_prerequisite, run_menu, view_prerequisites,
                        view_profile, view_unlocked)


def run_with_input(function, answers, *args):
    """Call function(*args) with input() returning answers in turn.

    Returns a pair: the function's return value and everything it printed.
    """
    output = io.StringIO()
    with patch("builtins.input", side_effect=answers):
        with redirect_stdout(output):
            result = function(*args)
    return result, output.getvalue()


class TestSampleCatalogue(unittest.TestCase):
    """The pre-loaded courses form a realistic, acyclic prerequisite web."""

    def setUp(self):
        """Build the sample graph and code lookup."""
        self.graph, self.courses_by_code = build_catalogue()

    def test_graph_and_lookup_match(self):
        """Between 5 and 10 courses, each in both the graph and the lookup."""
        vertices = self.graph.listVertices()
        self.assertTrue(5 <= len(vertices) <= 10)
        self.assertEqual(len(vertices), len(self.courses_by_code))
        for course in vertices:
            self.assertIs(self.courses_by_code[course.code], course)

    def test_all_sample_edges_loaded(self):
        """Every (prerequisite, course) pair is an edge in that direction."""
        for prerequisite_code, course_code in SAMPLE_PREREQUISITES:
            prerequisite = self.courses_by_code[prerequisite_code]
            course = self.courses_by_code[course_code]
            self.assertTrue(self.graph.hasEdge(prerequisite, course))

    def test_some_courses_both_require_and_are_required(self):
        """At least one course has prerequisites and also unlocks other courses."""
        in_the_middle = []
        for course in self.graph.listVertices():
            has_incoming = len(self.graph.listIncomingAdjacentVertex(course)) > 0
            has_outgoing = len(self.graph.listOutgoingAdjacentVertex(course)) > 0
            if has_incoming and has_outgoing:
                in_the_middle.append(course.code)
        self.assertIn("CS102", in_the_middle)
        self.assertIn("CS201", in_the_middle)

    def test_no_cycles(self):
        """For every edge u -> v there is no path back from v to u."""
        for prerequisite_code, course_code in SAMPLE_PREREQUISITES:
            prerequisite = self.courses_by_code[prerequisite_code]
            course = self.courses_by_code[course_code]
            self.assertFalse(self.graph.hasPath(course, prerequisite))


class TestMenuHelpers(unittest.TestCase):
    """Looking up codes and printing course lists."""

    def setUp(self):
        """Build the sample graph and code lookup."""
        self.graph, self.courses_by_code = build_catalogue()

    def test_ask_course_ignores_case(self):
        """A lower-case code finds the course."""
        course, output = run_with_input(ask_course, [" cs201 "], self.courses_by_code)
        self.assertEqual(course.code, "CS201")

    def test_ask_course_unknown_code(self):
        """An unknown code returns None with a message."""
        course, output = run_with_input(ask_course, ["XX999"], self.courses_by_code)
        self.assertIsNone(course)
        self.assertIn("No course with code 'XX999'", output)

    def test_ask_course_empty(self):
        """An empty answer returns None with a message."""
        course, output = run_with_input(ask_course, [""], self.courses_by_code)
        self.assertIsNone(course)
        self.assertIn("No course code entered", output)

    def test_course_list_is_sorted(self):
        """Courses are printed in code order whatever order they are given in."""
        courses = [self.courses_by_code["MA101"], self.courses_by_code["CS201"],
                   self.courses_by_code["CS101"]]
        result, output = run_with_input(print_course_list, [], courses)
        lines = output.splitlines()
        self.assertTrue(lines[0].strip().startswith("CS101"))
        self.assertTrue(lines[1].strip().startswith("CS201"))
        self.assertTrue(lines[2].strip().startswith("MA101"))

    def test_empty_course_list(self):
        """An empty list prints (none)."""
        result, output = run_with_input(print_course_list, [], [])
        self.assertEqual(output.strip(), "(none)")


class TestMenuOptions(unittest.TestCase):
    """The mandatory options show the right courses and survive bad input."""

    def setUp(self):
        """Build the sample graph and code lookup."""
        self.graph, self.courses_by_code = build_catalogue()

    def test_view_prerequisites(self):
        """CS301 needs CS201 and MA101, listed in code order."""
        result, output = run_with_input(view_prerequisites, ["CS301"],
                                        self.graph, self.courses_by_code)
        self.assertLess(output.index("CS201"), output.index("MA101"))
        self.assertNotIn("CS102", output)

    def test_view_unlocked(self):
        """CS102 unlocks CS201, CS202 and CS304."""
        result, output = run_with_input(view_unlocked, ["CS102"],
                                        self.graph, self.courses_by_code)
        for code in ["CS201", "CS202", "CS304"]:
            self.assertIn(code, output)

    def test_course_with_nothing_unlocked(self):
        """CS303 is not a prerequisite for anything."""
        result, output = run_with_input(view_unlocked, ["CS303"],
                                        self.graph, self.courses_by_code)
        self.assertIn("(none)", output)

    def test_menu_survives_bad_input(self):
        """Unknown options and codes are reported, and 0 exits normally."""
        answers = ["abc", "9", "", "2", "nope", "3", "", "7", "zz", "0"]
        result, output = run_with_input(run_menu, answers, self.graph, self.courses_by_code)
        self.assertIn("Please enter a number from 0 to 8.", output)
        self.assertIn("No course with code 'NOPE'", output)
        self.assertIn("Goodbye.", output)


class TestParsers(unittest.TestCase):
    """Each parse_ function returns a value for valid text and None otherwise."""

    def test_code(self):
        """Codes are upper-cased and must be 1-10 letters or digits."""
        self.assertEqual(parse_code("cs305"), "CS305")
        for text in ["", "CS 305", "CS-305", "A1234567890"]:
            self.assertIsNone(parse_code(text), text)

    def test_name(self):
        """Names must have 1 to 40 characters."""
        self.assertEqual(parse_name("Cloud Computing"), "Cloud Computing")
        self.assertIsNone(parse_name(""))
        self.assertIsNone(parse_name("x" * 41))

    def test_credit_hours(self):
        """Credit hours are whole numbers from 1 to 20."""
        self.assertEqual(parse_credit_hours("3"), 3)
        for text in ["", "four", "2.5", "0", "-1", "21"]:
            self.assertIsNone(parse_credit_hours(text), text)

    def test_level(self):
        """core/c and elective/e in any case; anything else is rejected."""
        self.assertEqual(parse_level("Core"), CORE)
        self.assertEqual(parse_level("c"), CORE)
        self.assertEqual(parse_level("ELECTIVE"), ELECTIVE)
        self.assertEqual(parse_level("e"), ELECTIVE)
        self.assertIsNone(parse_level("optional"))

    def test_read_value_retries(self):
        """read_value keeps asking until the answer is valid."""
        value, output = run_with_input(read_value, ["x", "0", "4"], "Credits",
                                       parse_credit_hours, "bad")
        self.assertEqual(value, 4)
        self.assertEqual(output.count("bad"), 2)


class TestProfile(unittest.TestCase):
    """The profile option respects each course's level."""

    def setUp(self):
        """Build the sample graph and code lookup."""
        self.graph, self.courses_by_code = build_catalogue()

    def test_elective_shows_name_only(self):
        """CS302 is an elective, so only its name is shown."""
        result, output = run_with_input(view_profile, ["CS302"], self.courses_by_code)
        self.assertIn("Web Development", output)
        self.assertNotIn("Credit hours", output)
        self.assertNotIn("Description", output)

    def test_core_shows_everything(self):
        """CS301 is core, so every field is shown."""
        result, output = run_with_input(view_profile, ["CS301"], self.courses_by_code)
        for text in ["CS301", "Advanced Algorithms", "Credit hours", "Core", "Description"]:
            self.assertIn(text, output)


class TestAddCourse(unittest.TestCase):
    """Adding a course validates input and rejects duplicate codes."""

    def setUp(self):
        """Build the sample graph and code lookup."""
        self.graph, self.courses_by_code = build_catalogue()

    def test_add_course_after_bad_answers(self):
        """Invalid answers are asked again; the course ends up in the graph and the lookup."""
        answers = ["cs305", "", "Cloud Computing", "four", "3", "maybe", "e",
                   "Containers and cloud services."]
        run_with_input(add_new_course, answers, self.graph, self.courses_by_code)
        course = self.courses_by_code["CS305"]
        self.assertTrue(self.graph.hasVertex(course))
        self.assertEqual(course.credit_hours, 3)
        self.assertEqual(course.level, ELECTIVE)
        self.assertEqual(self.graph.listIncomingAdjacentVertex(course), [])

    def test_duplicate_code_rejected(self):
        """An existing code is refused before any other question is asked."""
        result, output = run_with_input(add_new_course, ["cs201"],
                                        self.graph, self.courses_by_code)
        self.assertIn("already exists", output)
        self.assertEqual(self.courses_by_code["CS201"].name, "Data Structures")
        self.assertEqual(len(self.graph.listVertices()), 10)


class TestPrerequisiteRules(unittest.TestCase):
    """check_new_prerequisite rejects self-loops, duplicates and cycles."""

    def setUp(self):
        """Build the sample graph and code lookup."""
        self.graph, self.courses_by_code = build_catalogue()

    def check(self, prerequisite_code, course_code):
        """Return check_new_prerequisite's answer for two course codes."""
        return check_new_prerequisite(self.graph, self.courses_by_code[prerequisite_code],
                                      self.courses_by_code[course_code])

    def test_self_loop(self):
        """A course cannot be its own prerequisite."""
        self.assertIn("own prerequisite", self.check("CS201", "CS201"))

    def test_duplicate(self):
        """An existing prerequisite cannot be added again."""
        self.assertIn("already a prerequisite", self.check("CS101", "CS102"))

    def test_direct_cycle(self):
        """CS102 cannot be a prerequisite of CS101, because CS101 -> CS102 exists."""
        self.assertIn("cycle", self.check("CS102", "CS101"))

    def test_indirect_cycle(self):
        """CS303 cannot be a prerequisite of CS101: CS101 leads to CS303 through four edges."""
        self.assertIn("cycle", self.check("CS303", "CS101"))

    def test_allowed(self):
        """MA201 as a prerequisite of CS302 breaks no rule."""
        self.assertIsNone(self.check("MA201", "CS302"))


class TestPrerequisiteMenu(unittest.TestCase):
    """Adding and removing prerequisites through the menu."""

    def setUp(self):
        """Build the sample graph and code lookup."""
        self.graph, self.courses_by_code = build_catalogue()

    def assert_acyclic(self):
        """Check that no edge u -> v has a path back from v to u."""
        for course in self.graph.listVertices():
            for unlocked in self.graph.listOutgoingAdjacentVertex(course):
                self.assertFalse(self.graph.hasPath(unlocked, course))

    def test_add_prerequisite(self):
        """An allowed prerequisite becomes an edge."""
        result, output = run_with_input(add_prerequisite, ["cs302", "ma201"],
                                        self.graph, self.courses_by_code)
        self.assertTrue(self.graph.hasEdge(self.courses_by_code["MA201"],
                                           self.courses_by_code["CS302"]))
        self.assert_acyclic()

    def test_cycle_not_added(self):
        """A prerequisite that would create a cycle is refused and nothing changes."""
        result, output = run_with_input(add_prerequisite, ["CS101", "CS303"],
                                        self.graph, self.courses_by_code)
        self.assertIn("Not added", output)
        self.assertFalse(self.graph.hasEdge(self.courses_by_code["CS303"],
                                            self.courses_by_code["CS101"]))
        self.assert_acyclic()

    def test_unknown_code_adds_nothing(self):
        """An unknown prerequisite code stops the option without changes."""
        before = self.graph.listIncomingAdjacentVertex(self.courses_by_code["CS302"])
        run_with_input(add_prerequisite, ["CS302", "XX999"], self.graph, self.courses_by_code)
        after = self.graph.listIncomingAdjacentVertex(self.courses_by_code["CS302"])
        self.assertEqual(sorted(before), sorted(after))

    def test_remove_prerequisite(self):
        """Removing MA101 from CS301 deletes that edge only."""
        result, output = run_with_input(remove_prerequisite, ["CS301", "MA101"],
                                        self.graph, self.courses_by_code)
        cs301 = self.courses_by_code["CS301"]
        self.assertFalse(self.graph.hasEdge(self.courses_by_code["MA101"], cs301))
        self.assertTrue(self.graph.hasEdge(self.courses_by_code["CS201"], cs301))

    def test_remove_missing_prerequisite(self):
        """Removing a course that is not a prerequisite reports it and changes nothing."""
        result, output = run_with_input(remove_prerequisite, ["CS301", "CS101"],
                                        self.graph, self.courses_by_code)
        self.assertIn("is not a prerequisite", output)
        self.assertEqual(len(self.graph.listIncomingAdjacentVertex(self.courses_by_code["CS301"])), 2)

    def test_remove_from_course_without_prerequisites(self):
        """CS101 has no prerequisites, so nothing further is asked."""
        result, output = run_with_input(remove_prerequisite, ["CS101"],
                                        self.graph, self.courses_by_code)
        self.assertIn("has no prerequisites", output)


if __name__ == "__main__":
    unittest.main()
