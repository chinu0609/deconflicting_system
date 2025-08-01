import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json

from deconfliction_engine import DeconflictionEngine
from trajectory_calculator import TrajectoryCalculator
from visualization import VisualizationManager
from scenario_generator import ScenarioGenerator
from utils import format_time, calculate_distance_3d, validate_waypoints

# Page configuration
st.set_page_config(
    page_title="UAV Strategic Deconfliction System",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'deconfliction_engine' not in st.session_state:
    st.session_state.deconfliction_engine = DeconflictionEngine()
    st.session_state.trajectory_calculator = TrajectoryCalculator()
    st.session_state.visualization_manager = VisualizationManager()
    st.session_state.scenario_generator = ScenarioGenerator()
    st.session_state.current_scenario = None
    st.session_state.conflict_results = None
    st.session_state.animation_time = 0

def main():
    st.title("🚁 UAV Strategic Deconfliction System")
    st.markdown("### Interactive 3D Airspace Conflict Detection and Analysis")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Mission Configuration")
        
        # Scenario selection
        st.subheader("Select Scenario")
        scenario_options = {
            "Custom Mission": "custom",
            "Conflict-Free Mission": "conflict_free",
            "Spatial Conflict": "spatial_conflict",
            "Temporal Conflict": "temporal_conflict",
            "Complex Multi-Drone": "complex_scenario",
            "3D Altitude Conflict": "altitude_conflict"
        }
        
        selected_scenario = st.selectbox(
            "Choose a demonstration scenario:",
            options=list(scenario_options.keys())
        )
        
        if st.button("Load Scenario"):
            scenario_key = scenario_options[selected_scenario]
            if scenario_key == "custom":
                st.session_state.current_scenario = None
            else:
                st.session_state.current_scenario = st.session_state.scenario_generator.generate_scenario(scenario_key)
                st.success(f"Loaded {selected_scenario}")
                st.rerun()
        
        st.divider()
        
        # Mission parameters
        st.subheader("Mission Parameters")
        
        # Safety buffer
        safety_buffer = st.slider(
            "Safety Buffer (meters)",
            min_value=10.0,
            max_value=200.0,
            value=50.0,
            step=10.0,
            help="Minimum safe distance between drones"
        )
        
        # Time discretization
        time_step = st.slider(
            "Time Step (seconds)",
            min_value=1,
            max_value=30,
            value=5,
            help="Temporal resolution for conflict checking"
        )
        
        # 3D visualization toggle
        enable_3d = st.checkbox("Enable 3D Visualization", value=True)
        
        # Animation controls
        st.subheader("Animation Controls")
        if st.session_state.current_scenario:
            max_time = st.session_state.current_scenario.get('mission_duration', 300)
            current_time = st.slider(
                "Current Time (seconds)",
                min_value=0,
                max_value=max_time,
                value=st.session_state.animation_time,
                key="time_slider"
            )
            st.session_state.animation_time = current_time
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("▶️ Play"):
                    st.session_state.animation_playing = True
            with col2:
                if st.button("⏸️ Pause"):
                    st.session_state.animation_playing = False

    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Airspace Visualization")
        
        if st.session_state.current_scenario:
            # Generate trajectories and check conflicts
            primary_mission = st.session_state.current_scenario['primary_mission']
            other_flights = st.session_state.current_scenario['other_flights']
            
            # Calculate trajectories
            primary_trajectory = st.session_state.trajectory_calculator.calculate_trajectory(
                primary_mission['waypoints'],
                primary_mission['start_time'],
                primary_mission['end_time'],
                time_step
            )
            
            other_trajectories = []
            for flight in other_flights:
                traj = st.session_state.trajectory_calculator.calculate_trajectory(
                    flight['waypoints'],
                    flight['start_time'],
                    flight['end_time'],
                    time_step
                )
                other_trajectories.append({
                    'trajectory': traj,
                    'flight_id': flight['flight_id']
                })
            
            # Perform deconfliction analysis
            st.session_state.conflict_results = st.session_state.deconfliction_engine.check_conflicts(
                primary_trajectory,
                other_trajectories,
                safety_buffer
            )
            
            # Create visualization
            fig = st.session_state.visualization_manager.create_airspace_plot(
                primary_trajectory,
                other_trajectories,
                st.session_state.conflict_results,
                current_time=st.session_state.animation_time,
                enable_3d=enable_3d
            )
            
            st.plotly_chart(fig, use_container_width=True, height=600)
            
        else:
            st.info("Please select and load a scenario to begin visualization.")
            
            # Manual mission input
            st.subheader("Manual Mission Input")
            
            # Waypoint input
            st.write("Enter mission waypoints (format: x,y,z,time):")
            waypoint_input = st.text_area(
                "Waypoints",
                value="0,0,50,0\n100,0,50,60\n100,100,75,120\n0,100,50,180\n0,0,50,240",
                height=150,
                help="Each line should contain: x,y,z,time (in seconds)"
            )
            
            # Time window
            col_start, col_end = st.columns(2)
            with col_start:
                start_time = st.number_input("Mission Start Time (s)", value=0, min_value=0)
            with col_end:
                end_time = st.number_input("Mission End Time (s)", value=300, min_value=1)
            
            if st.button("Create Custom Mission"):
                try:
                    waypoints = []
                    for line in waypoint_input.strip().split('\n'):
                        if line.strip():
                            parts = [float(x.strip()) for x in line.split(',')]
                            if len(parts) >= 4:
                                waypoints.append({
                                    'x': parts[0],
                                    'y': parts[1],
                                    'z': parts[2] if len(parts) > 2 else 50,
                                    'time': parts[3] if len(parts) > 3 else 0
                                })
                    
                    if validate_waypoints(waypoints):
                        custom_scenario = st.session_state.scenario_generator.create_custom_scenario(
                            waypoints, start_time, end_time
                        )
                        st.session_state.current_scenario = custom_scenario
                        st.success("Custom mission created successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid waypoint format. Please check your input.")
                        
                except Exception as e:
                    st.error(f"Error creating mission: {str(e)}")
    
    with col2:
        st.subheader("Conflict Analysis")
        
        if st.session_state.conflict_results:
            conflicts = st.session_state.conflict_results['conflicts']
            
            if conflicts:
                st.error(f"🚨 {len(conflicts)} Conflict(s) Detected")
                
                for i, conflict in enumerate(conflicts):
                    with st.expander(f"Conflict {i+1}: {conflict['type'].title()}"):
                        st.write(f"**Location:** ({conflict['location']['x']:.1f}, {conflict['location']['y']:.1f}, {conflict['location']['z']:.1f})")
                        st.write(f"**Time:** {format_time(conflict['time'])}")
                        st.write(f"**Distance:** {conflict['distance']:.1f}m")
                        st.write(f"**Conflicting Flight:** {conflict['other_flight_id']}")
                        st.write(f"**Severity:** {conflict['severity']}")
                        
                        if conflict['description']:
                            st.write(f"**Description:** {conflict['description']}")
            else:
                st.success("✅ No Conflicts Detected")
                st.write("Mission is clear for execution.")
        
        else:
            st.info("Load a scenario to begin conflict analysis.")
        
        # Mission statistics
        if st.session_state.current_scenario:
            st.subheader("Mission Statistics")
            
            primary_mission = st.session_state.current_scenario['primary_mission']
            other_flights = st.session_state.current_scenario['other_flights']
            
            st.metric("Total Waypoints", len(primary_mission['waypoints']))
            st.metric("Mission Duration", f"{primary_mission['end_time'] - primary_mission['start_time']}s")
            st.metric("Other Flights", len(other_flights))
            
            # Mission details
            with st.expander("Mission Details"):
                st.write("**Primary Mission Waypoints:**")
                waypoint_df = pd.DataFrame(primary_mission['waypoints'])
                st.dataframe(waypoint_df, use_container_width=True)
                
                st.write("**Other Flights:**")
                for flight in other_flights:
                    st.write(f"- {flight['flight_id']}: {len(flight['waypoints'])} waypoints")

    # Bottom section for additional controls and export
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Regenerate Scenario"):
            if st.session_state.current_scenario:
                scenario_type = st.session_state.current_scenario.get('type', 'conflict_free')
                st.session_state.current_scenario = st.session_state.scenario_generator.generate_scenario(scenario_type)
                st.success("Scenario regenerated!")
                st.rerun()
    
    with col2:
        if st.button("📊 Export Analysis"):
            if st.session_state.conflict_results:
                analysis_data = {
                    'timestamp': datetime.now().isoformat(),
                    'scenario': st.session_state.current_scenario,
                    'conflicts': st.session_state.conflict_results['conflicts'],
                    'parameters': {
                        'safety_buffer': safety_buffer,
                        'time_step': time_step
                    }
                }
                
                st.download_button(
                    label="Download Analysis",
                    data=json.dumps(analysis_data, indent=2),
                    file_name=f"deconfliction_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    with col3:
        if st.button("🎥 Generate Demo Video"):
            st.info("Video generation feature would be implemented here. This would create an animated sequence showing the conflict detection process.")

if __name__ == "__main__":
    main()
