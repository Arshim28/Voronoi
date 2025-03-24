import random
import matplotlib.pyplot as plt
import numpy as np

def visualize_voronoi(voronoi, output_file=None, show_labels=False, title=None, dpi=300):
    """
    Visualize a Voronoi diagram and save it to a file.
    
    Args:
        voronoi: The Voronoi diagram object
        output_file: Optional file name to save the visualization
        show_labels: Whether to show labels for sites and vertices
        title: Optional title for the plot
        dpi: Resolution of the output image
        
    Returns:
        The file path if saved, otherwise None
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    
    min_x = voronoi.bounding_poly.min_x
    max_x = voronoi.bounding_poly.max_x
    min_y = voronoi.bounding_poly.min_y
    max_y = voronoi.bounding_poly.max_y
    
    # Plot bounding polygon
    polygon_coords = voronoi.bounding_poly.get_coordinates()
    polygon = plt.Polygon(polygon_coords, fill=False, edgecolor='black')
    ax.add_patch(polygon)
    
    # Plot edges
    for edge in voronoi.edges:
        start = edge.get_origin()
        end = edge.twin.get_origin()
        if start and end:
            ax.plot([start.x, end.x], [start.y, end.y], 'b-')
    
    # Plot sites (points)        
    xs = [point.x for point in voronoi.sites]
    ys = [point.y for point in voronoi.sites]
    ax.scatter(xs, ys, color='red', s=50, zorder=5)
    
    # Add labels if requested
    if show_labels:
        for point in voronoi.sites:
            ax.text(float(point.x), float(point.y) + 0.2, f"P{point.name}", fontsize=8)
            
        for i, vertex in enumerate(voronoi.vertices):
            ax.text(float(vertex.x), float(vertex.y), f"V{i}", fontsize=6, color='blue')
    
    # Set plot limits with some padding
    padding = (max_x - min_x) * 0.05
    ax.set_xlim(min_x - padding, max_x + padding)
    ax.set_ylim(min_y - padding, max_y + padding)
    ax.set_aspect('equal')
    
    # Set title
    if title:
        ax.set_title(title)
    else:
        ax.set_title('Voronoi Diagram')
    
    # Save to file if specified
    if output_file:
        plt.savefig(output_file, dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        return output_file
    else:
        plt.show()
        return None

def create_voronoi_diagram(points, bounding_polygon=None):
    """
    Create a Voronoi diagram from a set of points.
    
    Args:
        points: List of (x, y) coordinates
        bounding_polygon: Optional list of (x, y) coordinates defining the bounding polygon
        
    Returns:
        A Voronoi diagram object
    """
    from polygon import Polygon
    from voronoi import Voronoi
    
    if bounding_polygon is None:
        # Create default bounding box
        min_x = min(p[0] for p in points) - 2
        max_x = max(p[0] for p in points) + 2
        min_y = min(p[1] for p in points) - 2
        max_y = max(p[1] for p in points) + 2
        bounding_polygon = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
    
    # Create a polygon for bounding
    polygon = Polygon(bounding_polygon)
    
    # Initialize the algorithm
    v = Voronoi(polygon)
    
    # Create the diagram
    v.create_diagram(points=points)
    
    return v

def generate_random_points(n, min_x=0, max_x=100, min_y=0, max_y=100):
    """Generate n random points within the specified bounds"""
    return [(random.uniform(min_x, max_x), random.uniform(min_y, max_y)) for _ in range(n)]

def generate_grid_points(rows, cols, min_x=0, max_x=100, min_y=0, max_y=100):
    """Generate a grid of evenly spaced points"""
    x_step = (max_x - min_x) / (cols - 1) if cols > 1 else 0
    y_step = (max_y - min_y) / (rows - 1) if rows > 1 else 0
    
    points = []
    for i in range(rows):
        for j in range(cols):
            x = min_x + j * x_step
            y = min_y + i * y_step
            points.append((x, y))
    
    return points

def generate_circle_points(n, center_x=50, center_y=50, radius=40):
    """Generate points arranged in a circle"""
    points = []
    for i in range(n):
        angle = 2 * np.pi * i / n
        x = center_x + radius * np.cos(angle)
        y = center_y + radius * np.sin(angle)
        points.append((x, y))
    return points