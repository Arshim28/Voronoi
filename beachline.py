import numpy as np
from geometry import Coordinate

class Arc:
    def __init__(self, origin: Coordinate, circle_event=None):
        self.origin = origin
        self.circle_event = circle_event

    def __repr__(self):
        return f"Arc({self.origin.name})"

    def get_plot(self, x, sweep_line):
        sweep_line = float(sweep_line)
        i = self.origin
        if i.y - sweep_line == 0:
            return None
        u = 2 * (i.y - sweep_line)
        v = (x ** 2 - 2 * i.x * x + i.x ** 2 + i.y ** 2 - sweep_line ** 2)
        y = v/u
        return y

class Breakpoint:
    def __init__(self, breakpoint: tuple, edge=None):
        self.breakpoint = breakpoint
        self._edge = None
        self.edge = edge

    def __repr__(self):
        return f"Breakpoint({self.breakpoint[0].name}, {self.breakpoint[1].name})"

    def does_intersect(self):
        i, j = self.breakpoint
        return not (i.y == j.y and j.x < i.x)

    def get_intersection(self, l, max_y=None):
        i, j = self.breakpoint
        result = Coordinate()
        p: Coordinate = i
        a = i.x
        b = i.y
        c = j.x
        d = j.y
        u = 2 * (b - l)
        v = 2 * (d - l)
        
        if i.y == j.y:
            result.x = (i.x + j.x) / 2
            if j.x < i.x:
                result.y = max_y or float('inf')
                return result
        elif i.y == l:
            result.x = i.x
            p = j
        elif j.y == l:
            result.x = j.x
        else:
            if abs(u - v) < 1e-10:
                result.x = (a + c) / 2
            else:
                discriminant = v * (a**2 * u - 2*a*c*u + b**2*(u-v) + c**2*u) + d**2*u*(v-u) + l**2*(u-v)**2
                if discriminant < 0:
                    discriminant = 0
                
                x = -(np.sqrt(discriminant) + a*v - c*u) / (u - v)
                result.x = x
                
        a = p.x
        b = p.y
        x = result.x
        u = 2 * (b - l)
        
        if abs(u) < 1e-10:
            result.y = float("inf")
            return result
            
        result.y = 1 / u * (x ** 2 - 2 * a * x + a ** 2 + b ** 2 - l ** 2)
        return result

    @property
    def edge(self):
        return self._edge

    @edge.setter
    def edge(self, value):
        self._edge = value