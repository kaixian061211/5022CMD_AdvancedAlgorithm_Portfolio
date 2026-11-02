class Graph:
    """Unweighted directed graph whose vertices can be any hashable value.

    Adjacency is stored in both directions as a dict of sets:
      outgoing[v] is the set of vertices that v has an edge to;
      incoming[v] is the set of vertices that have an edge to v.
    Keeping both makes listing either direction a direct lookup, instead of
    a scan over every vertex. The two dicts are always changed together.

    Method names follow the camelCase names required by the brief.
    """

    def __init__(self):
        """Create an empty graph."""
        self.outgoing = {}
        self.incoming = {}

    def _checkVertex(self, vertex):
        """Raise KeyError if vertex is not in the graph."""
        if vertex not in self.outgoing:
            raise KeyError(f"vertex not in graph: {vertex!r}")

    def addVertex(self, vertex):
        """Add a vertex with no edges. Return True, or False if it was already present."""
        if vertex in self.outgoing:
            return False
        self.outgoing[vertex] = set()
        self.incoming[vertex] = set()
        return True

    def hasVertex(self, vertex):
        """Return True if vertex is in the graph."""
        return vertex in self.outgoing

    def listVertices(self):
        """Return a list of all vertices, in the order they were added."""
        return list(self.outgoing)

    def addEdge(self, source, target):
        """Add the directed edge source -> target.

        Returns True, or False if the edge already exists. Both vertices must
        already be in the graph, otherwise KeyError is raised, so a mistyped
        vertex is reported instead of being added silently.
        """
        self._checkVertex(source)
        self._checkVertex(target)
        if target in self.outgoing[source]:
            return False
        self.outgoing[source].add(target)
        self.incoming[target].add(source)
        return True

    def hasEdge(self, source, target):
        """Return True if the directed edge source -> target exists."""
        return source in self.outgoing and target in self.outgoing[source]

    def removeEdge(self, source, target):
        """Remove the directed edge source -> target. Return True, or False if it did not exist."""
        if not self.hasEdge(source, target):
            return False
        self.outgoing[source].remove(target)
        self.incoming[target].remove(source)
        return True

    def listOutgoingAdjacentVertex(self, vertex):
        """Return a list of the vertices that vertex has an edge to.

        A new list is returned, so changing it cannot change the graph.
        Raises KeyError if vertex is not in the graph.
        """
        self._checkVertex(vertex)
        return list(self.outgoing[vertex])

    def listIncomingAdjacentVertex(self, vertex):
        """Return a list of the vertices that have an edge to vertex.

        A new list is returned, so changing it cannot change the graph.
        Raises KeyError if vertex is not in the graph.
        """
        self._checkVertex(vertex)
        return list(self.incoming[vertex])

    def hasPath(self, source, target):
        """Return True if target can be reached from source by following edges.

        Uses depth-first search: the stack is last-in, first-out, so the search
        follows one route as far as it goes before trying another. A vertex
        reaches itself by a path with no edges. The visited set stops the
        search going round a cycle forever and means each vertex is expanded
        at most once, so the search is O(V + E).
        Raises KeyError if either vertex is not in the graph.
        """
        self._checkVertex(source)
        self._checkVertex(target)
        visited = set()
        stack = [source]
        while stack:
            vertex = stack.pop()
            if vertex == target:
                return True
            if vertex in visited:
                continue
            visited.add(vertex)
            for neighbour in self.outgoing[vertex]:
                if neighbour not in visited:
                    stack.append(neighbour)
        return False
