import numpy as np
from geometry import Coordinate

class Event:
    circle_event = False

    @property
    def x(self):
        return 0

    @property
    def y(self):
        return 0

    def __lt__(self, other):
        if self.y == other.y and self.x == other.x:
            return self.circle_event and not other.circle_event
        if self.y == other.y:
            return self.x < other.x
        return self.y > other.y

    def __eq__(self, other):
        if other is None:
            return None
        return self.y == other.y and self.x == other.x

    def __ne__(self, other):
        return not self.__eq__(other)

class SiteEvent(Event):
    circle_event = False

    def __init__(self, point):
        self.point = point

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y

    def __repr__(self):
        return f"SiteEvent(x={self.point.x}, y={self.point.y})"

class CircleEvent(Event):
    circle_event = True

    def __init__(self, center: Coordinate, radius: float, arc_node, point_triple=None, arc_triple=None):
        self.center = center
        self.radius = radius
        self.arc_pointer = arc_node
        self.is_valid = True
        self.point_triple = point_triple
        self.arc_triple = arc_triple

    def __repr__(self):
        return f"CircleEvent({self.point_triple}, y-radius={self.center.y - self.radius:.2f}, y={self.center.y:.2f}, radius={self.radius:.2f})"

    @property
    def x(self):
        return self.center.x

    @property
    def y(self):
        return self.center.y - self.radius

    def _get_triangle(self):
        return (
            (self.point_triple[0].x, self.point_triple[0].y),
            (self.point_triple[1].x, self.point_triple[1].y),
            (self.point_triple[2].x, self.point_triple[2].y),
        )

    def remove(self):
        self.is_valid = False
        return self

    @staticmethod
    def create_circle_event(left_node, middle_node, right_node, sweep_line):
        if left_node is None or right_node is None or middle_node is None:
            return None
        left_arc = left_node.get_value()
        middle_arc = middle_node.get_value()
        right_arc = right_node.get_value()
        a, b, c = left_arc.origin, middle_arc.origin, right_arc.origin
        if CircleEvent.create_circle(a, b, c):
            x, y, radius = CircleEvent.create_circle(a, b, c)
            return CircleEvent(center=Coordinate(x, y), radius=radius, arc_node=middle_node, point_triple=(a, b, c),
                               arc_triple=(left_arc, middle_arc, right_arc))
        return None

    @staticmethod
    def create_circle(a, b, c):
        A = b.x - a.x
        B = b.y - a.y
        C = c.x - a.x
        D = c.y - a.y
        E = (b.x - a.x) * (a.x + b.x) + (b.y - a.y) * (a.y + b.y)
        F = (c.x - a.x) * (a.x + c.x) + (c.y - a.y) * (a.y + c.y)
        G = 2 * ((b.x - a.x) * (c.y - b.y) - (b.y - a.y) * (c.x - b.x))
        
        if abs(G) < 1e-10:
            return False
            
        x = (D * E - B * F) / G
        y = (A * F - C * E) / G
        
        radius = np.sqrt((a.x - x) ** 2 + (a.y - y) ** 2)
        return x, y, radius