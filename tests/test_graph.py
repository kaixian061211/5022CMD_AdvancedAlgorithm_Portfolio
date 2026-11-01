import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "q2_graph"))

from graph import Graph


class Keyed:
    """A test vertex that, like Course, is equal to any Keyed with the same key."""

    def __init__(self, key, label):
        """Store the key used for equality and a label that is not."""
        self.key = key
        self.label = label

    def __eq__(self, other):
        """Equal when the keys match."""
        return isinstance(other, Keyed) and self.key == other.key

    def __hash__(self):
        """Hash on the key, so equal objects have equal hashes."""
        return hash(self.key)


class TestVertices(unittest.TestCase):
    """Adding, checking and listing vertices."""

    def setUp(self):
        """Start each test with an empty graph."""
        self.graph = Graph()

    def test_add_vertex(self):
        """A new vertex is added and can be found."""
        self.assertTrue(self.graph.addVertex("A"))
        self.assertTrue(self.graph.hasVertex("A"))
        self.assertFalse(self.graph.hasVertex("B"))

    def test_add_duplicate_vertex(self):
        """Adding the same vertex twice returns False and keeps one copy."""
        self.graph.addVertex("A")
        self.assertFalse(self.graph.addVertex("A"))
        self.assertEqual(self.graph.listVertices(), ["A"])

    def test_list_vertices_in_insertion_order(self):
        """Vertices are listed in the order they were added."""
        for vertex in ["C", "A", "B"]:
            self.graph.addVertex(vertex)
        self.assertEqual(self.graph.listVertices(), ["C", "A", "B"])

    def test_new_vertex_has_no_edges(self):
        """A vertex starts with empty incoming and outgoing lists."""
        self.graph.addVertex("A")
        self.assertEqual(self.graph.listIncomingAdjacentVertex("A"), [])
        self.assertEqual(self.graph.listOutgoingAdjacentVertex("A"), [])

    def test_generic_vertices(self):
        """Any hashable value can be a vertex; an unhashable one cannot."""
        self.graph.addVertex(1)
        self.graph.addVertex((2, 3))
        self.graph.addEdge(1, (2, 3))
        self.assertEqual(self.graph.listOutgoingAdjacentVertex(1), [(2, 3)])
        with self.assertRaises(TypeError):
            self.graph.addVertex([4])

    def test_equal_objects_are_one_vertex(self):
        """Objects equal by key count as the same vertex, as Course objects will."""
        self.graph.addVertex(Keyed("CS101", "first object"))
        self.assertFalse(self.graph.addVertex(Keyed("CS101", "second object")))
        self.assertTrue(self.graph.hasVertex(Keyed("CS101", "any label")))


class TestEdges(unittest.TestCase):
    """Edges are directed and kept in both adjacency dicts."""

    def setUp(self):
        """Start each test with vertices A, B and C and no edges."""
        self.graph = Graph()
        for vertex in ["A", "B", "C"]:
            self.graph.addVertex(vertex)

    def test_add_edge_updates_both_directions(self):
        """A -> B shows as outgoing from A and incoming to B."""
        self.assertTrue(self.graph.addEdge("A", "B"))
        self.assertEqual(self.graph.listOutgoingAdjacentVertex("A"), ["B"])
        self.assertEqual(self.graph.listIncomingAdjacentVertex("B"), ["A"])

    def test_edge_is_directed(self):
        """A -> B does not create B -> A."""
        self.graph.addEdge("A", "B")
        self.assertTrue(self.graph.hasEdge("A", "B"))
        self.assertFalse(self.graph.hasEdge("B", "A"))
        self.assertEqual(self.graph.listIncomingAdjacentVertex("A"), [])
        self.assertEqual(self.graph.listOutgoingAdjacentVertex("B"), [])

    def test_duplicate_edge(self):
        """Adding an existing edge returns False and keeps one copy."""
        self.graph.addEdge("A", "B")
        self.assertFalse(self.graph.addEdge("A", "B"))
        self.assertEqual(self.graph.listIncomingAdjacentVertex("B"), ["A"])

    def test_several_edges(self):
        """A vertex can have several incoming and outgoing edges."""
        self.graph.addEdge("A", "C")
        self.graph.addEdge("B", "C")
        self.graph.addEdge("A", "B")
        self.assertEqual(sorted(self.graph.listIncomingAdjacentVertex("C")), ["A", "B"])
        self.assertEqual(sorted(self.graph.listOutgoingAdjacentVertex("A")), ["B", "C"])

    def test_edge_needs_existing_vertices(self):
        """An edge to or from a missing vertex raises KeyError and adds nothing."""
        with self.assertRaises(KeyError):
            self.graph.addEdge("A", "Z")
        with self.assertRaises(KeyError):
            self.graph.addEdge("Z", "A")
        self.assertFalse(self.graph.hasVertex("Z"))
        self.assertEqual(self.graph.listOutgoingAdjacentVertex("A"), [])

    def test_self_loop_allowed(self):
        """The generic graph allows A -> A; the course menu is what forbids it."""
        self.assertTrue(self.graph.addEdge("A", "A"))
        self.assertEqual(self.graph.listIncomingAdjacentVertex("A"), ["A"])

    def test_remove_edge(self):
        """Removing A -> B clears it from both directions."""
        self.graph.addEdge("A", "B")
        self.assertTrue(self.graph.removeEdge("A", "B"))
        self.assertFalse(self.graph.hasEdge("A", "B"))
        self.assertEqual(self.graph.listOutgoingAdjacentVertex("A"), [])
        self.assertEqual(self.graph.listIncomingAdjacentVertex("B"), [])

    def test_remove_missing_edge(self):
        """Removing an edge that does not exist returns False."""
        self.assertFalse(self.graph.removeEdge("A", "B"))
        self.assertFalse(self.graph.removeEdge("A", "Z"))

    def test_lists_for_missing_vertex(self):
        """Asking for the neighbours of a missing vertex raises KeyError."""
        with self.assertRaises(KeyError):
            self.graph.listIncomingAdjacentVertex("Z")
        with self.assertRaises(KeyError):
            self.graph.listOutgoingAdjacentVertex("Z")

    def test_returned_list_is_a_copy(self):
        """Changing a returned list does not change the graph."""
        self.graph.addEdge("A", "B")
        self.graph.listOutgoingAdjacentVertex("A").append("C")
        self.graph.listIncomingAdjacentVertex("B").clear()
        self.assertFalse(self.graph.hasEdge("A", "C"))
        self.assertTrue(self.graph.hasEdge("A", "B"))


class TestHasPath(unittest.TestCase):
    """hasPath follows edge directions and copes with cycles."""

    def setUp(self):
        """Build A -> B -> C -> D, plus A -> C, and a separate vertex E."""
        self.graph = Graph()
        for vertex in ["A", "B", "C", "D", "E"]:
            self.graph.addVertex(vertex)
        self.graph.addEdge("A", "B")
        self.graph.addEdge("B", "C")
        self.graph.addEdge("C", "D")
        self.graph.addEdge("A", "C")

    def test_direct_edge(self):
        """One edge is a path."""
        self.assertTrue(self.graph.hasPath("A", "B"))

    def test_path_over_several_edges(self):
        """A reaches D through B and C."""
        self.assertTrue(self.graph.hasPath("A", "D"))
        self.assertTrue(self.graph.hasPath("B", "D"))

    def test_direction_matters(self):
        """Edges only lead forwards, so D cannot reach A."""
        self.assertFalse(self.graph.hasPath("D", "A"))
        self.assertFalse(self.graph.hasPath("C", "B"))

    def test_unconnected_vertex(self):
        """E has no edges, so nothing reaches it and it reaches nothing else."""
        self.assertFalse(self.graph.hasPath("A", "E"))
        self.assertFalse(self.graph.hasPath("E", "A"))

    def test_vertex_reaches_itself(self):
        """A path with no edges leads from a vertex to itself."""
        self.assertTrue(self.graph.hasPath("E", "E"))

    def test_search_ends_in_a_cycle(self):
        """With a cycle B -> C -> B, a search for an unreachable vertex still finishes."""
        self.graph.addEdge("C", "B")
        self.assertFalse(self.graph.hasPath("B", "E"))
        self.assertTrue(self.graph.hasPath("D", "D"))

    def test_detects_edge_that_would_close_a_cycle(self):
        """Adding D -> A would close the cycle A -> ... -> D -> A, because hasPath(A, D)."""
        self.assertTrue(self.graph.hasPath("A", "D"))
        self.assertFalse(self.graph.hasPath("D", "A"))

    def test_missing_vertex(self):
        """Either vertex missing raises KeyError."""
        with self.assertRaises(KeyError):
            self.graph.hasPath("A", "Z")
        with self.assertRaises(KeyError):
            self.graph.hasPath("Z", "A")


if __name__ == "__main__":
    unittest.main()
