# UAV Strategic Deconfliction System

A comprehensive web application for detecting and analyzing potential conflicts between drone flight paths in 3D airspace. Built with Streamlit for interactive visualization and real-time conflict analysis.

## Features

- **3D Interactive Visualization** - Real-time 3D airspace visualization with drone trajectories
- **Conflict Detection** - Advanced spatial and temporal conflict detection algorithms
- **Multiple Scenarios** - Pre-built scenarios for testing various conflict types
- **Custom Mission Planning** - Define your own waypoint missions
- **Real-time Animation** - Time-based animation showing drone movements
- **Detailed Analysis** - Comprehensive conflict reports with severity levels
- **Export Capabilities** - Export analysis results for further processing

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Quick Setup

1. **Clone or download the project**
   ```bash
   git clone https://github.com/chinu0609/deconflicting_system.git
   cd deconflicting_system
   ```

2. **Install dependencies**
   ```bash
   uv sync --frozen
   ```

3. **Run the application**
   Activate the env and 
   ```bash
   streamlit run app.py --server.port 5000
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000` to access the application.


## User Interface Guide

### Main Interface Layout

The application is divided into three main sections:

#### 1. Sidebar Controls (Left Panel)

**Mission Configuration**
- **Scenario Selection**: Choose from predefined scenarios or create custom missions
- **Load Scenario Button**: Loads the selected scenario and initializes visualization

**Mission Parameters**
- **Safety Buffer Slider**: Adjust the minimum safe distance between drones (10-200 meters)
- **Time Step Slider**: Set temporal resolution for conflict checking (1-30 seconds)
- **3D Visualization Toggle**: Switch between 3D and 2D top-down views

**Animation Controls**
- **Time Slider**: Scrub through mission timeline to see drone positions at any time
- **Play/Pause Buttons**: Control real-time animation playback

#### 2. Main Visualization Area (Center)

**Airspace Display**
- **Interactive 3D Plot**: Shows all drone trajectories with the ability to rotate, zoom, and pan
- **Primary Mission**: Blue solid line representing your main drone's planned route
- **Other Flights**: Orange dotted lines showing other aircraft in the airspace
- **Current Positions**: Diamond and circle markers showing real-time drone locations
- **Conflict Zones**: Red spheres or circles highlighting areas where conflicts occur

**Plot Controls**
- **Mouse Interactions**: 
  - Left click + drag: Rotate view
  - Right click + drag: Pan
  - Scroll wheel: Zoom in/out
- **Hover Information**: Detailed position and timing data for each trajectory point

#### 3. Analysis Panel (Right Panel)

**Conflict Analysis**
- **Status Indicator**: Green checkmark for safe missions, red warning for conflicts
- **Conflict Details**: Expandable sections showing:
  - Conflict location coordinates
  - Time of occurrence
  - Distance between aircraft
  - Severity level (LOW/MEDIUM/HIGH)
  - Involved flight IDs

**Mission Statistics**
- **Total Waypoints**: Number of waypoints in primary mission
- **Mission Duration**: Total time to complete the mission
- **Other Flights**: Count of other aircraft in the airspace

**Mission Details** (Expandable)
- **Waypoint Table**: Detailed coordinates and timing for each waypoint
- **Flight Roster**: List of all other flights with waypoint counts

### Bottom Controls

**Action Buttons**
- **🔄 Regenerate Scenario**: Create a new random scenario of the same type
- **📊 Export Analysis**: Download complete analysis results as JSON file
- **🎥 Generate Demo Video**: (Feature placeholder) Would create animated demonstration videos

## How It Works

### 1. Mission Input

The system accepts drone missions defined by:
- **Waypoints**: 3D coordinates (x, y, z) with timing information
- **Time Window**: Overall mission start and end times
- **Flight Parameters**: Speed constraints and trajectory smoothing

### 2. Trajectory Calculation

**Process:**
1. **Waypoint Normalization**: Adjusts waypoint times to fit mission window
2. **Interpolation**: Creates smooth flight paths between waypoints
3. **Temporal Discretization**: Samples positions at regular time intervals
4. **Speed Calculation**: Determines realistic flight speeds for each segment

### 3. Conflict Detection

**Spatial Analysis:**
- Calculates 3D distance between all drone pairs at each time step
- Compares distances against configurable safety buffer
- Identifies proximity violations in real-time

**Temporal Analysis:**
- Tracks when multiple drones occupy similar airspace
- Detects temporal overlaps in shared flight corridors
- Analyzes timing conflicts for sequential airspace usage

### 4. Conflict Classification

**Severity Levels:**
- **HIGH**: Distance < 50% of safety buffer (immediate danger)
- **MEDIUM**: Distance < 80% of safety buffer (caution required)
- **LOW**: Distance < 100% of safety buffer (monitoring needed)

**Conflict Types:**
- **Spatial**: Direct proximity conflicts in 3D space
- **Temporal**: Time-based conflicts in shared areas
- **Trajectory**: Intersection of planned flight paths

### 5. Visualization and Analysis

**Real-time Display:**
- 3D visualization of all trajectories
- Animated drone positions over time
- Highlighted conflict zones with safety buffers
- Interactive timeline scrubbing

**Analysis Reports:**
- Detailed conflict descriptions
- Timing and location information
- Severity assessments
- Resolution recommendations

## Predefined Scenarios

### 1. Conflict-Free Mission
- **Purpose**: Demonstrates safe, well-separated flight paths
- **Features**: Multiple drones with adequate spacing
- **Use Case**: Baseline for safe operations

### 2. Spatial Conflict
- **Purpose**: Shows direct trajectory crossings
- **Features**: Drone paths intersect in 3D space
- **Use Case**: Testing proximity detection algorithms

### 3. Temporal Conflict
- **Purpose**: Demonstrates time-based conflicts
- **Features**: Sequential use of same airspace corridor
- **Use Case**: Validating temporal separation logic

### 4. Complex Multi-Drone
- **Purpose**: Advanced scenario with multiple conflict types
- **Features**: 3+ drones with various interaction patterns
- **Use Case**: Comprehensive system testing

### 5. 3D Altitude Conflict
- **Purpose**: Focuses on vertical separation issues
- **Features**: Conflicts primarily in altitude domain
- **Use Case**: Testing 3D spatial analysis

## Custom Mission Creation

### Manual Waypoint Input

1. **Select "Custom Mission"** from scenario dropdown
2. **Enter waypoints** in the text area using format: `x,y,z,time`
   ```
   Example:
   0,0,50,0
   100,0,50,60
   100,100,75,120
   0,100,50,180
   0,0,50,240
   ```
3. **Set mission timing** with start and end time inputs
4. **Click "Create Custom Mission"** to generate the scenario

### Waypoint Format

- **x, y**: Horizontal coordinates in meters
- **z**: Altitude in meters (typically 30-120m)
- **time**: Time offset in seconds from mission start

## Technical Architecture

### Core Components

1. **DeconflictionEngine**: Central conflict detection system
2. **TrajectoryCalculator**: Converts waypoints to detailed flight paths
3. **VisualizationManager**: Handles all plotting and animation
4. **ScenarioGenerator**: Creates predefined test scenarios
5. **Utils**: Mathematical functions and data validation

### Data Flow

1. **Input**: Waypoint missions and parameters
2. **Processing**: Trajectory calculation and conflict analysis
3. **Visualization**: Real-time 3D plotting with Plotly
4. **Output**: Conflict reports and safety recommendations

## Troubleshooting

### Common Issues

**Application won't start:**
- Ensure Python 3.11+ is installed
- Check that all dependencies are installed: `pip install streamlit numpy pandas plotly`
- Verify port 5000 is available

**Visualization not displaying:**
- Check browser JavaScript is enabled
- Try refreshing the page
- Ensure scenario is loaded before expecting visualization

**Poor performance with animations:**
- Reduce time step resolution (increase time step value)
- Switch to 2D visualization mode
- Limit the number of other flights in custom scenarios

### Performance Optimization

- **Large datasets**: Increase time step to reduce trajectory points
- **Slow rendering**: Disable 3D mode for faster 2D visualization
- **Memory usage**: Limit mission duration and number of concurrent flights

## Export and Integration

### Analysis Export

The system can export complete analysis results including:
- Mission parameters and waypoints
- Detected conflicts with full details
- Timing and spatial analysis
- Safety recommendations

### File Format

Exported data is in JSON format for easy integration with other systems:

```json
{
  "metadata": {
    "timestamp": "2025-01-01T12:00:00",
    "scenario_type": "spatial_conflict"
  },
  "mission": {
    "primary_waypoints": [...],
    "duration": 240
  },
  "analysis": {
    "conflicts": [...],
    "is_safe": false
  }
}
```

## Future Enhancements

### Planned Features

- **Video Export**: Automated generation of demonstration videos
- **Real-time Data Integration**: Connect to live drone tracking systems
- **Advanced Algorithms**: Machine learning-based conflict prediction
- **Multi-user Support**: Collaborative mission planning interface
- **Mobile Optimization**: Responsive design for tablet/mobile use

### Scalability Considerations

For production deployment with thousands of drones:
- **Distributed Computing**: Cluster-based conflict detection
- **Database Integration**: Persistent storage for mission history
- **Real-time Streaming**: WebSocket-based live updates
- **Caching Systems**: Redis for frequently accessed trajectory data
- **Load Balancing**: Multiple server instances for high availability

## Support and Documentation

### Getting Help

- Check this README for common issues
- Review the code comments for technical details
- Ensure all dependencies are properly installed
- Verify input data formats match specifications

### Contributing

The system is designed with modular components for easy extension:
- Add new scenario types in `scenario_generator.py`
- Extend conflict detection algorithms in `deconfliction_engine.py`
- Create custom visualization modes in `visualization.py`
- Add utility functions in `utils.py`

---

**Built with AI assistance for rapid development and comprehensive functionality.**
