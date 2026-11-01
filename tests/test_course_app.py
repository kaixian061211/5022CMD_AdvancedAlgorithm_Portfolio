import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "q2_graph"))

from course_app import (SAMPLE_PREREQUISITES, ask_course, build_catalogue,
                        print_course_list, run_menu, view_prerequisites,
                        view_unlocked)


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
        answers = ["abc", "9", "", "2", "nope", "3", "", "0"]
        result, output = run_with_input(run_menu, answers, self.graph, self.courses_by_code)
        self.assertIn("Please enter a number from 0 to 4.", output)
        self.assertIn("No course with code 'NOPE'", output)
        self.assertIn("Goodbye.", output)


if __name__ == "__main__":
    unittest.main()
