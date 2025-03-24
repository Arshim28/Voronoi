import os
import sys
import json
import argparse
from utils import (
    create_voronoi_diagram,
    visualize_voronoi,
    generate_random_points,
    generate_grid_points,
    generate_circle_points
)

def parse_args():
    parser = argparse.ArgumentParser(description='Generate Voronoi diagram from input points')
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--file', type=str, help='JSON file containing points and optionally a bounding polygon')
    input_group.add_argument('--random', type=int, help='Generate N random points')
    input_group.add_argument('--grid', type=str, help='Generate a grid of points, format: ROWSxCOLUMNS')
    input_group.add_argument('--circle', type=int, help='Generate N points arranged in a circle')
    
    parser.add_argument('--output', type=str, help='Output PNG file', required=True)
    parser.add_argument('--labels', action='store_true', help='Show labels on the diagram')
    parser.add_argument('--title', type=str, help='Title for the diagram')
    parser.add_argument('--dpi', type=int, default=300, help='Resolution of the output image')
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Generate or load points
    if args.file:
        with open(args.file, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, dict):
            points = data.get('points', [])
            bounding_polygon = data.get('bounding_polygon', None)
        else:
            points = data
            bounding_polygon = None
            
    elif args.random:
        points = generate_random_points(args.random)
        bounding_polygon = None
        
    elif args.grid:
        try:
            rows, cols = map(int, args.grid.split('x'))
            points = generate_grid_points(rows, cols)
            bounding_polygon = None
        except ValueError:
            print("Error: Grid format should be ROWSxCOLUMNS, e.g., 5x5")
            return 1
            
    elif args.circle:
        points = generate_circle_points(args.circle)
        bounding_polygon = None
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create and visualize the Voronoi diagram
    voronoi = create_voronoi_diagram(points, bounding_polygon)
    output_file = visualize_voronoi(
        voronoi, 
        output_file=args.output,
        show_labels=args.labels,
        title=args.title,
        dpi=args.dpi
    )
    
    print(f"Voronoi diagram saved to {output_file}")
    
    # Print statistics
    print(f"Number of points: {len(points)}")
    print(f"Number of vertices: {len(voronoi.vertices)}")
    print(f"Number of edges: {len(voronoi.edges)}")
    
    # Print area information
    areas = [point.area() for point in voronoi.sites]
    print(f"Min area: {min(areas):.2f}")
    print(f"Max area: {max(areas):.2f}")
    print(f"Average area: {sum(areas)/len(areas):.2f}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())