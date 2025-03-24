import numpy as np
from geometry import Coordinate, Vertex, HalfEdge

class Polygon:
    def __init__(self, tuples):
        points = [Coordinate(x, y) for x, y in tuples]
        self.points = points
        min_y = min([p.y for p in self.points])
        min_x = min([p.x for p in self.points])
        max_y = max([p.y for p in self.points])
        max_x = max([p.x for p in self.points])
        center = Coordinate((max_x + min_x) / 2, (max_y + min_y) / 2)
        self.min_y, self.min_x, self.max_y, self.max_x, self.center = min_y, min_x, max_y, max_x, center
        self.points = self._order_points(self.points)
        self.polygon_vertices = []
        for point in self.points:
            self.polygon_vertices.append(Vertex(point.x, point.y))

    def _order_points(self, points):
        clockwise = sorted(points, key=lambda point: (-180 - self._calculate_angle(point, self.center)) % 360)
        return clockwise

    def _calculate_angle(self, point, center):
        dx = float(point.x - center.x)
        dy = float(point.y - center.y)
        return np.degrees(np.arctan2(dy, dx)) % 360

    def _get_ordered_vertices(self, vertices):
        vertices = [vertex for vertex in vertices if vertex.x is not None]
        clockwise = sorted(vertices,
                           key=lambda vertex: (-180 - self._calculate_angle(vertex, self.center)) % 360)
        return clockwise

    def finish_polygon(self, edges, existing_vertices, points):
        vertices = self._get_ordered_vertices(self.polygon_vertices)
        vertices = list(vertices) + [vertices[0]]
        cell = self._get_closest_point(vertices[0], points)
        previous_edge = None
        for index in range(0, len(vertices) - 1):
            origin = vertices[index]
            end = vertices[index + 1]
            if len(origin.connected_edges) > 0:
                cell = origin.connected_edges[0].twin.incident_point
            edge = HalfEdge(cell, origin=origin, twin=HalfEdge(None, origin=end))
            origin.connected_edges.append(edge)
            end.connected_edges.append(edge.twin)
            if cell:
                cell.first_edge = cell.first_edge or edge
            if len(end.connected_edges) > 0:
                edge.set_next(end.connected_edges[0])
            elif previous_edge is not None:
                previous_edge.set_next(edge)
            edges.append(edge)
            previous_edge = edge
        existing_vertices = [i for i in existing_vertices if self.inside(i)]
        return edges, vertices[:-1] + existing_vertices

    def _get_closest_point(self, position, points):
        distances = [self._distance(position, p) for p in points]
        index = np.argmin(distances)
        return points[index]

    def _distance(self, point_a, point_b):
        x1 = point_a.x
        x2 = point_b.x
        y1 = point_a.y
        y2 = point_b.y
        return np.sqrt((x2 - x1) ** 2 + (y2 - y1)**2)

    def finish_edges(self, edges, vertices=None, points=None, event_queue=None):
        resulting_edges = []
        for edge in edges:
            if edge.get_origin() is None or not self.inside(edge.get_origin()):
                self._finish_edge(edge)
            if edge.twin.get_origin() is None or not self.inside(edge.twin.get_origin()):
                self._finish_edge(edge.twin)
            if edge.get_origin() is not None and edge.twin.get_origin() is not None:
                resulting_edges.append(edge)
            else:
                edge.delete()
                edge.twin.delete()
        return resulting_edges

    def _finish_edge(self, edge):
        sweep_line = self.min_y - abs(self.max_y)
        start = edge.get_origin(y=sweep_line, max_y=self.max_y)
        end = edge.twin.get_origin(y=sweep_line, max_y=self.max_y)
        point = self._get_intersection_point(end, start)
        v = Vertex(point.x, point.y) if point is not None else Vertex(None, None)
        v.connected_edges.append(edge)
        edge.origin = v
        self.polygon_vertices.append(v)
        return edge

    def _get_intersection_point(self, orig, end):
        p = self.points + [self.points[0]]
        points = []
        point = None
        for i in range(0, len(p) - 1):
            intersection_point = self._get_intersection(orig, end, p[i], p[i + 1])
            if intersection_point:
                points.append(intersection_point)
        if not points:
            return None
        max_distance = self._distance(orig, end)
        if points:
            distances = [self._distance(orig, p) for p in points]
            distances = [i for i in distances if i <= max_distance]
            if distances:
                point = points[np.argmax(distances)]
        return point

    def _get_intersection(self, orig, end, p1, p2):
        if not orig or not end:
            return None
        point = self._line_ray_intersection_point([orig.x, orig.y], [end.x, end.y], [p1.x, p1.y], [p2.x, p2.y])
        if len(point) == 0:
            return None
        return Coordinate(point[0][0], point[0][1])

    def _magnitude(self, vector):
        return np.sqrt(np.dot(np.array(vector), np.array(vector)))

    def _norm(self, vector):
        mag = self._magnitude(np.array(vector))
        if mag < 1e-10:
            return np.array(vector)
        return np.array(vector) / mag

    def _line_ray_intersection_point(self, ray_orig, ray_end, point_1, point_2):
        orig = np.array(ray_orig, dtype=np.float64)
        end = np.array(ray_end, dtype=np.float64)
        direction = np.array(self._norm(end - orig), dtype=np.float64)
        point_1 = np.array(point_1, dtype=np.float64)
        point_2 = np.array(point_2, dtype=np.float64)
        v1 = orig - point_1
        v2 = point_2 - point_1
        v3 = np.array([-direction[1], direction[0]])
        
        dot_prod = np.dot(v2, v3)
        if abs(dot_prod) < 1e-10:
            return []
            
        t1 = np.cross(v2, v1) / dot_prod
        t2 = np.dot(v1, v3) / dot_prod
        
        if t1 > 0.0 and 0.0 <= t2 <= 1.0:
            return [orig + t1 * direction]
        return []

    def inside(self, point):
        vertices = self.points + self.points[0:1]
        x = point.x
        y = point.y
        inside = False
        for i in range(0, len(vertices) - 1):
            j = i + 1
            xi = vertices[i].x
            yi = vertices[i].y
            xj = vertices[j].x
            yj = vertices[j].y
            intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi)
            if intersect:
                inside = not inside
        return inside
        
    def get_coordinates(self):
        return [(i.x, i.y) for i in self.points]