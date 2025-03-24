from queue import PriorityQueue
from typing import List, Set, Tuple

import numpy as np

from geometry import Vertex, Point, HalfEdge, Coordinate
from events import SiteEvent, CircleEvent
from beachline import Arc, Breakpoint
from tree import Tree, LeafNode, InternalNode, Node
from polygon import Polygon

class Voronoi:
    def __init__(self, bounding_poly: Polygon = None, remove_zero_length_edges=True):
        self.bounding_poly = bounding_poly
        self.event_queue = PriorityQueue()
        self.event = None
        self.status_tree = None
        self.doubly_connected_edge_list = []
        self.sweep_line = float("inf")
        self._arcs = set()
        self.sites = None
        self.edges = list()
        self._vertices = set()
        self.remove_zero_length_edges = remove_zero_length_edges

    @property
    def arcs(self) -> List[Arc]:
        return list(self._arcs)

    @property
    def vertices(self) -> List[Vertex]:
        return list(self._vertices)

    def initialize(self, points):
        self.sites = points
        for index, point in enumerate(points):
            site_event = SiteEvent(point=point)
            self.event_queue.put(site_event)
        return self.event_queue

    def create_diagram(self, points: list):
        points = [Point(x, y) for x, y in points]
        self.initialize(points)
        index = 0
        genesis_point = None
        while not self.event_queue.empty():
            event = self.event_queue.get()
            genesis_point = genesis_point or getattr(event, 'point', None)
            if isinstance(event, CircleEvent) and event.is_valid:
                self.sweep_line = event.y
                self.handle_circle_event(event)
            elif isinstance(event, SiteEvent):
                event.point.name = index
                index += 1
                self.sweep_line = event.y
                self.handle_site_event(event)
            else:
                continue
            self.event = event
        self.edges = self.bounding_poly.finish_edges(
            edges=self.edges, vertices=self._vertices, points=self.sites, event_queue=self.event_queue
        )
        self.edges, self._vertices = self.bounding_poly.finish_polygon(self.edges, self._vertices, self.sites)
        if self.remove_zero_length_edges:
            self.clean_up_zero_length_edges()

    def handle_site_event(self, event: SiteEvent):
        point_i = event.point
        new_arc = Arc(origin=point_i)
        self._arcs.add(new_arc)
        if self.status_tree is None:
            self.status_tree = LeafNode(new_arc)
            return
        arc_node_above_point = Tree.find_leaf_node(self.status_tree, key=point_i.x, sweep_line=self.sweep_line)
        arc_above_point = arc_node_above_point.get_value()
        if arc_above_point.circle_event is not None:
            arc_above_point.circle_event.remove()
        point_j = arc_above_point.origin
        breakpoint_left = Breakpoint(breakpoint=(point_j, point_i))
        breakpoint_right = Breakpoint(breakpoint=(point_i, point_j))
        root = InternalNode(breakpoint_left)
        root.left = LeafNode(Arc(origin=point_j, circle_event=None))
        if breakpoint_right.does_intersect():
            root.right = InternalNode(breakpoint_right)
            root.right.left = LeafNode(new_arc)
            root.right.right = LeafNode(Arc(origin=point_j, circle_event=None))
        else:
            root.right = LeafNode(new_arc)
        self.status_tree = arc_node_above_point.replace_leaf(replacement=root, root=self.status_tree)
        A, B = point_j, point_i
        AB = breakpoint_left
        BA = breakpoint_right
        AB.edge = HalfEdge(B, origin=AB)
        BA.edge = HalfEdge(A, origin=BA, twin=AB.edge)
        self.edges.append(AB.edge)
        B.first_edge = B.first_edge or AB.edge
        A.first_edge = A.first_edge or BA.edge
        if not breakpoint_right.does_intersect():
            return
        node_a, node_b, node_c = root.left.predecessor, root.left, root.right.left
        node_c, node_d, node_e = node_c, root.right.right, root.right.right.successor
        self._check_circles((node_a, node_b, node_c), (node_c, node_d, node_e))
        self.status_tree = Tree.balance_and_propagate(root)

    def handle_circle_event(self, event: CircleEvent):
        arc = event.arc_pointer.data
        if arc in self._arcs:
            self._arcs.remove(arc)
        arc_node: LeafNode = event.arc_pointer
        predecessor = arc_node.predecessor
        successor = arc_node.successor
        self.status_tree, updated, removed, left, right = self._update_breakpoints(
            self.status_tree, self.sweep_line, arc_node, predecessor, successor)
        if updated is None:
            return
        def remove(neighbor_event):
            if neighbor_event is None:
                return None
            return neighbor_event.remove()
        remove(predecessor.get_value().circle_event)
        remove(successor.get_value().circle_event)
        convergence_point = event.center
        v = Vertex(convergence_point.x, convergence_point.y)
        self._vertices.add(v)
        updated.edge.origin = v
        removed.edge.origin = v
        v.connected_edges.append(updated.edge)
        v.connected_edges.append(removed.edge)
        breakpoint_a = updated.breakpoint[0]
        breakpoint_b = updated.breakpoint[1]
        new_edge = HalfEdge(breakpoint_a, origin=v, twin=HalfEdge(breakpoint_b, origin=updated))
        left.edge.twin.set_next(new_edge)
        right.edge.twin.set_next(left.edge)
        new_edge.twin.set_next(right.edge)
        self.edges.append(new_edge)
        v.connected_edges.append(new_edge)
        updated.edge = new_edge.twin
        former_left = predecessor
        former_right = successor
        node_a, node_b, node_c = former_left.predecessor, former_left, former_left.successor
        node_d, node_e, node_f = former_right.predecessor, former_right, former_right.successor
        self._check_circles((node_a, node_b, node_c), (node_d, node_e, node_f))

    def _check_circles(self, triple_left, triple_right):
        node_a, node_b, node_c = triple_left
        node_d, node_e, node_f = triple_right
        left_event = CircleEvent.create_circle_event(node_a, node_b, node_c, sweep_line=self.sweep_line)
        right_event = CircleEvent.create_circle_event(node_d, node_e, node_f, sweep_line=self.sweep_line)
        if left_event:
            if not self._check_clockwise(node_a.data.origin, node_b.data.origin, node_c.data.origin,
                                     left_event.center):
                left_event = None
        if right_event:
            if not self._check_clockwise(node_d.data.origin, node_e.data.origin, node_f.data.origin,
                                      right_event.center):
                right_event = None
        if left_event is not None:
            self.event_queue.put(left_event)
            node_b.data.circle_event = left_event
        if right_event is not None and left_event != right_event:
            self.event_queue.put(right_event)
            node_e.data.circle_event = right_event
        return left_event, right_event

    def _check_clockwise(self, a, b, c, center):
        angle_1 = self._calculate_angle(a, center)
        angle_2 = self._calculate_angle(b, center)
        angle_3 = self._calculate_angle(c, center)
        counter_clockwise = (angle_3 - angle_1) % 360 > (angle_3 - angle_2) % 360
        if counter_clockwise:
            return False
        return True

    def _calculate_angle(self, point, center):
        dx = float(point.x - center.x)
        dy = float(point.y - center.y)
        return np.degrees(np.arctan2(dy, dx)) % 360

    @staticmethod
    def _update_breakpoints(root, sweep_line, arc_node, predecessor, successor):
        if arc_node.is_left_child():
            root = arc_node.parent.replace_leaf(arc_node.parent.right, root)
            removed = arc_node.parent.data
            right = removed
            root = Tree.balance_and_propagate(root)
            left_breakpoint = Breakpoint(breakpoint=(predecessor.get_value().origin, arc_node.get_value().origin))
            query = InternalNode(left_breakpoint)
            compare = lambda x, y: hasattr(x, "breakpoint") and x.breakpoint == y.breakpoint
            breakpoint: InternalNode = Tree.find_value(root, query, compare, sweep_line=sweep_line)
            if breakpoint is not None:
                breakpoint.data.breakpoint = (breakpoint.get_value().breakpoint[0], successor.get_value().origin)
            updated = breakpoint.data if breakpoint is not None else None
            left = updated
        else:
            root = arc_node.parent.replace_leaf(arc_node.parent.left, root)
            removed = arc_node.parent.data
            left = removed
            root = Tree.balance_and_propagate(root)
            right_breakpoint = Breakpoint(breakpoint=(arc_node.get_value().origin, successor.get_value().origin))
            query = InternalNode(right_breakpoint)
            compare = lambda x, y: hasattr(x, "breakpoint") and x.breakpoint == y.breakpoint
            breakpoint: InternalNode = Tree.find_value(root, query, compare, sweep_line=sweep_line)
            if breakpoint is not None:
                breakpoint.data.breakpoint = (predecessor.get_value().origin, breakpoint.get_value().breakpoint[1])
            updated = breakpoint.data if breakpoint is not None else None
            right = updated
        return root, updated, removed, left, right

    def clean_up_zero_length_edges(self):
        resulting_edges = []
        for edge in self.edges:
            start = edge.get_origin()
            end = edge.twin.get_origin()
            # Use epsilon comparison for floating-point equality
            if start and end and abs(start.x - end.x) < 1e-10 and abs(start.y - end.y) < 1e-10:
                v1: Vertex = edge.origin
                v2: Vertex = edge.twin.origin
                for connected in list(v1.connected_edges):  # Use a copy of the list
                    connected.origin = v2
                    if connected in v1.connected_edges:  # Check if it's still in the list
                        v1.connected_edges.remove(connected)
                    v2.connected_edges.append(connected)
                if v1 in self._vertices:  # Check if it's in the set
                    self._vertices.remove(v1)
                edge.delete()
                edge.twin.delete()
            else:
                resulting_edges.append(edge)
        self.edges = resulting_edges