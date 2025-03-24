# Voronoi Diagram Module
from geometry import Coordinate, Point, Vertex, HalfEdge
from polygon import Polygon
from events import Event, SiteEvent, CircleEvent
from beachline import Arc, Breakpoint
from tree import Node, LeafNode, InternalNode, Tree
from voronoi import Voronoi
from utils import (
    create_voronoi_diagram,
    visualize_voronoi,
    generate_random_points,
    generate_grid_points,
    generate_circle_points
)

__version__ = '1.0.0'