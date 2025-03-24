# Voronoi Diagram Generator

A Python implementation of Fortune's algorithm for generating Voronoi diagrams.

## Installation

This project uses Python 3.11+ and uv as the package manager.

1. Install uv (if not already installed):
   ```bash
   curl -sS https://raw.githubusercontent.com/astral-sh/uv/main/install.sh | bash
   ```

2. Clone the repository

3. Install dependencies:
   ```bash
   uv venv .venv
   source .venv/bin/activate
   uv sync
   ```

## Usage

### Command Line Interface

```bash
# Generate a diagram with 10 random points
uv run main.py --random 10 --output output.png

# Generate a diagram with a 4x4 grid of points
uv run main.py --grid 4x4 --output grid.png

# Generate a diagram with 8 points arranged in a circle
uv run main.py --circle 8 --output circle.png --labels

# Use a JSON file with custom points
uv run main.py --file sample_points.json --output custom.png --title "Custom Points"
```

### JSON Input Format

```json
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
```

## Running Tests

Run all tests with the provided script:
```bash
./test.sh
```

Run specific test cases:
```bash
# Run all tests in TestGeometry class
uv run tests.py TestGeometry

# Run a specific test method
uv run tests.py TestVoronoi.test_simple_diagram
```

## Output Examples

The program generates PNG images of Voronoi diagrams with optional labels and titles.

- Random points: `output_random.png`
- Grid points: `output_grid.png`
- Circle points: `output_circle.png`
- Custom JSON input: `output_json.png`

## Implementation Details

This implementation uses Fortune's algorithm for generating Voronoi diagrams:

- `geometry.py`: Basic geometric primitives
- `voronoi.py`: Main implementation of Fortune's algorithm
- `beachline.py`: Beach line data structure
- `events.py`: Site and circle event handling
- `polygon.py`: Bounding polygon implementation
- `utils.py`: Utility functions for generation and visualization
