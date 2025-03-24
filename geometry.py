import numpy as np

class Coordinate:
    def __init__(self, x=None, y=None):
        self._x = np.float64(x) if x is not None else None
        self._y = np.float64(y) if y is not None else None

    def __sub__(self, other):
        return Coordinate(x=self.x - other.x, y=self.y - other.y)

    def __repr__(self):
        return f"Coord({self.x:.2f}, {self.y:.2f})"

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @x.setter
    def x(self, value):
        self._x = np.float64(value)

    @y.setter
    def y(self, value):
        self._y = np.float64(value)

    @property
    def xy(self):
        return self.x, self.y

class Vertex(Coordinate):
    def __init__(self, x, y, connected_edges=None):
        super().__init__(x, y)
        self.connected_edges = connected_edges or []

    def __repr__(self):
        return f"Vertex({self.x:.2f}, {self.y:.2f})"

class Point(Coordinate):
    def __init__(self, x=None, y=None, name=None, first_edge=None):
        super().__init__(x, y)
        self.name = name
        self.first_edge = first_edge

    def __repr__(self):
        if self.name is not None:
            return f"P{self.name}"
        return f"Point({self.x:.2f}, {self.y:.2f})"

    @staticmethod
    def _shoelace(x, y):
        return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

    def area(self, digits=None):
        x, y = self._get_xy()
        if digits is not None:
            return round(self._shoelace(x, y), digits)
        return float(self._shoelace(x, y))

    def borders(self):
        if self.first_edge is None:
            return []
        edge = self.first_edge
        edges = [edge]
        while edge.next != self.first_edge:
            if edge.next is None:
                return edges
            edge = edge.next
            edges.append(edge)
        return edges

    def vertices(self):
        borders = self.borders()
        if borders is None:
            return None
        return [border.origin for border in borders if isinstance(border.origin, Vertex)]

    def _get_xy(self):
        coordinates = self.vertices()
        if coordinates is None:
            return [], []
        x = [coordinate.x for coordinate in coordinates]
        y = [coordinate.y for coordinate in coordinates]
        return x, y

    def __sub__(self, other):
        return Point(x=self.x - other.x, y=self.y - other.y)

class HalfEdge:
    def __init__(self, incident_point, twin=None, origin=None):
        self.origin = origin
        self.incident_point = incident_point
        self._twin = None
        self.twin = twin
        self.next = None
        self.prev = None
        self.removed = False

    def __repr__(self):
        return f"{self.incident_point}/{self.twin.incident_point or '-'}"

    def set_next(self, next):
        if next:
            next.prev = self
        self.next = next

    def get_origin(self, y=None, max_y=None):
        if isinstance(self.origin, Vertex):
            if self.origin.x is None or self.origin.y is None:
                return None
            return self.origin
        if y is not None:
            return self.origin.get_intersection(y, max_y=max_y)
        return None

    @property
    def twin(self):
        return self._twin

    @twin.setter
    def twin(self, twin):
        if twin is not None:
            twin._twin = self
        self._twin = twin

    @property
    def target(self):
        if self.twin is None:
            return None
        return self.twin.origin

    def delete(self):
        if isinstance(self.origin, Vertex):
            self.origin.connected_edges.remove(self)
        if self.prev is not None:
            self.prev.set_next(self.next)
        if self.incident_point is not None and self.incident_point.first_edge == self:
            self.incident_point.first_edge = self.next