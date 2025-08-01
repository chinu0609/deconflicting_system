# UAV Strategic Deconfliction System

## Overview

The UAV Strategic Deconfliction System is a comprehensive web application for detecting and analyzing potential conflicts between drone flight paths in 3D airspace. Built with Streamlit for the web interface and Plotly for interactive visualizations, the system performs spatial and temporal conflict detection, generates various flight scenarios for testing, and provides real-time 3D visualization of airspace with multiple drone trajectories.

The application allows users to define custom waypoint missions or select from predefined scenarios to analyze potential conflicts between a primary drone mission and other aircraft in the airspace. It calculates detailed flight trajectories, identifies safety violations, and visualizes the results through interactive 3D plots with animation capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Framework**: Web-based user interface providing interactive controls and real-time visualization
- **Session State Management**: Maintains application state across user interactions, storing engine instances and current scenario data
- **Modular UI Components**: Sidebar configuration panel for mission setup and main content area for visualization and results

### Core Processing Components
- **DeconflictionEngine**: Central conflict detection system that performs spatial and temporal analysis between drone trajectories using 3D distance calculations and safety buffer zones
- **TrajectoryCalculator**: Converts waypoint missions into detailed flight paths with temporal interpolation, speed calculations, and heading determination
- **ScenarioGenerator**: Creates predefined test scenarios including conflict-free missions, spatial conflicts, temporal conflicts, and complex multi-drone scenarios
- **VisualizationManager**: Handles all plotting and animation functionality using Plotly for both 2D and 3D airspace representations

### Data Processing Pipeline
- **Waypoint-to-Trajectory Conversion**: Transforms discrete waypoints into continuous flight paths with configurable time discretization
- **Conflict Detection Algorithm**: Pairwise analysis of trajectories using 3D Euclidean distance calculations with safety buffer enforcement
- **Real-time Animation**: Time-based position interpolation for dynamic visualization of drone movements

### Utility Functions
- **3D Spatial Calculations**: Distance calculations, position interpolation, and geometric analysis functions
- **Time Management**: Temporal formatting, mission duration calculations, and time-based trajectory sampling
- **Data Validation**: Waypoint validation and trajectory integrity checks

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework for the user interface
- **Plotly**: Interactive plotting library for 3D visualization and animations (plotly.graph_objects and plotly.express)
- **NumPy**: Numerical computing for mathematical operations and array handling
- **Pandas**: Data manipulation and analysis for trajectory data management

### Python Standard Libraries
- **datetime**: Time and date handling for mission scheduling
- **json**: Data serialization for configuration management
- **math**: Mathematical functions for geometric calculations
- **typing**: Type hints for code documentation and validation

### Visualization Components
- **Plotly Graph Objects**: 3D scatter plots, line traces, and animation frames
- **Plotly Express**: Simplified plotting interface for quick visualizations
- **Color Management**: Predefined color palette for consistent visual representation of different trajectory types and conflict states