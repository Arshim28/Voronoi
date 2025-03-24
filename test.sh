#!/bin/bash

# Exit on error
set -e

# Run unit tests
echo "Running unit tests..."
uv run tests.py

# Test with random points
echo "Testing with random points..."
uv run main.py --random 10 --output output_random.png

# Test with grid points
echo "Testing with grid points..."
uv run main.py --grid 4x4 --output output_grid.png

# Test with circle points
echo "Testing with circle points..."
uv run main.py --circle 8 --output output_circle.png --labels

# Create a JSON test file
echo "Creating sample JSON input..."
cat > sample_points.json << EOL
{
  "points": [
    [10, 10],
    [20, 40],
    [30, 10],
    [40, 40],
    [50, 10]
  ],
  "bounding_polygon": [
    [0, 0],
    [60, 0],
    [60, 50],
    [0, 50]
  ]
}
EOL

# Test with JSON file
echo "Testing with JSON input..."
uv run main.py --file sample_points.json --output output_json.png --title "JSON Input Test"

echo "All tests completed successfully!"
echo "Output images: output_random.png, output_grid.png, output_circle.png, output_json.png"