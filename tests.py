import unittest
import numpy as np
from geometry import Coordinate, Point, HalfEdge, Vertex
from polygon import Polygon
from events import CircleEvent
from utils import create_voronoi_diagram, generate_random_points

class TestGeometry(unittest.TestCase):
    def test_coordinate(self):
        c = Coordinate(1.0, 2.0)
        self.assertEqual(c.x, 1.0)
        self.assertEqual(c.y, 2.0)
        
        c2 = Coordinate(3.0, 4.0)
        diff = c - c2
        self.assertEqual(diff.x, -2.0)
        self.assertEqual(diff.y, -2.0)
    
    def test_point(self):
        p = Point(1.0, 2.0, name="test")
        self.assertEqual(p.name, "test")
        self.assertEqual(str(p), "Ptest")
        
        p_noname = Point(1.0, 2.0)
        self.assertTrue("Point" in str(p_noname))

class TestPolygon(unittest.TestCase):
    def test_polygon_creation(self):
        poly = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        self.assertEqual(poly.min_x, 0)
        self.assertEqual(poly.max_x, 10)
        self.assertEqual(poly.min_y, 0)
        self.assertEqual(poly.max_y, 10)
        self.assertEqual(len(poly.points), 4)
        
    def test_inside(self):
        poly = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
        inside_point = Coordinate(5, 5)
        outside_point = Coordinate(15, 15)
        self.assertTrue(poly.inside(inside_point))
        self.assertFalse(poly.inside(outside_point))

class TestVoronoi(unittest.TestCase):
    def test_simple_diagram(self):
        points = [(1, 1), (5, 5), (9, 1)]
        diagram = create_voronoi_diagram(points)
        self.assertEqual(len(diagram.sites), 3)
        
        # The diagram should have vertices
        # Note: Our implementation includes boundary vertices where edges 
        # intersect the bounding polygon, so there will typically be more 
        # vertices than just the internal ones
        self.assertGreater(len(diagram.vertices), 0)
        
    def test_circle_event(self):
        a = Coordinate(0, 0)
        b = Coordinate(1, 0)
        c = Coordinate(0.5, 1)
        
        x, y, r = CircleEvent.create_circle(a, b, c)
        self.assertAlmostEqual(x, 0.5, places=6)
        self.assertAlmostEqual(y, 0.375, places=6)  # The correct y-coordinate is 0.375
        self.assertAlmostEqual(r, np.sqrt(0.390625), places=6)  # Radius is approximately 0.625

class TestUtilities(unittest.TestCase):
    def test_random_points(self):
        n = 10
        points = generate_random_points(n)
        self.assertEqual(len(points), n)
        
        # Check that all points are within bounds
        for x, y in points:
            self.assertGreaterEqual(x, 0)
            self.assertLessEqual(x, 100)
            self.assertGreaterEqual(y, 0)
            self.assertLessEqual(y, 100)

if __name__ == '__main__':
    unittest.main()