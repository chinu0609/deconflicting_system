import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import List, Dict, Any
import pandas as pd

class VisualizationManager:
    """
    Manages all visualization components for the UAV deconfliction system.
    Creates interactive 3D plots, animations, and conflict highlighting.
    """
    
    def __init__(self):
        self.color_palette = {
            'primary': '#1f77b4',     # Blue
            'other': '#ff7f0e',       # Orange
            'conflict': '#d62728',    # Red
            'safe': '#2ca02c',        # Green
            'waypoint': '#9467bd',    # Purple
            'zone': '#e377c2'         # Pink
        }
        
    def create_airspace_plot(self, primary_trajectory: List[Dict], 
                           other_trajectories: List[Dict], 
                           conflict_results: Dict, 
                           current_time: float = 0,
                           enable_3d: bool = True) -> go.Figure:
        """
        Create main airspace visualization with all trajectories and conflicts.
        """
        fig = go.Figure()
        
        if enable_3d:
            fig = self._create_3d_plot(primary_trajectory, other_trajectories, 
                                     conflict_results, current_time)
        else:
            fig = self._create_2d_plot(primary_trajectory, other_trajectories, 
                                     conflict_results, current_time)
        
        # Update layout
        fig.update_layout(
            title="UAV Airspace Deconfliction Visualization",
            font=dict(size=12),
            margin=dict(l=0, r=0, t=50, b=0),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        return fig
    
    def _create_3d_plot(self, primary_trajectory: List[Dict], 
                       other_trajectories: List[Dict], 
                       conflict_results: Dict, 
                       current_time: float) -> go.Figure:
        """
        Create 3D airspace visualization.
        """
        fig = go.Figure()
        
        # Add primary trajectory
        if primary_trajectory:
            primary_df = pd.DataFrame(primary_trajectory)
            
            # Full trajectory path
            fig.add_trace(go.Scatter3d(
                x=primary_df['x'],
                y=primary_df['y'],
                z=primary_df['z'],
                mode='lines+markers',
                line=dict(color=self.color_palette['primary'], width=6),
                marker=dict(size=3),
                name='Primary Mission',
                hovertemplate="<b>Primary Mission</b><br>" +
                            "Position: (%{x:.1f}, %{y:.1f}, %{z:.1f})<br>" +
                            "Time: %{text}s<extra></extra>",
                text=primary_df['time']
            ))
            
            # Current position marker
            current_pos = self._get_position_at_time(primary_trajectory, current_time)
            if current_pos:
                fig.add_trace(go.Scatter3d(
                    x=[current_pos['x']],
                    y=[current_pos['y']],
                    z=[current_pos['z']],
                    mode='markers',
                    marker=dict(
                        size=12,
                        color=self.color_palette['primary'],
                        symbol='diamond'
                    ),
                    name=f'Primary @ {current_time}s',
                    showlegend=False
                ))
        
        # Add other trajectories
        for i, traj_data in enumerate(other_trajectories):
            trajectory = traj_data['trajectory']
            flight_id = traj_data['flight_id']
            
            if trajectory:
                traj_df = pd.DataFrame(trajectory)
                
                fig.add_trace(go.Scatter3d(
                    x=traj_df['x'],
                    y=traj_df['y'],
                    z=traj_df['z'],
                    mode='lines+markers',
                    line=dict(color=self.color_palette['other'], width=4, dash='dot'),
                    marker=dict(size=2),
                    name=f'Flight {flight_id}',
                    hovertemplate=f"<b>Flight {flight_id}</b><br>" +
                                "Position: (%{x:.1f}, %{y:.1f}, %{z:.1f})<br>" +
                                "Time: %{text}s<extra></extra>",
                    text=traj_df['time']
                ))
                
                # Current position for other drones
                current_pos = self._get_position_at_time(trajectory, current_time)
                if current_pos:
                    fig.add_trace(go.Scatter3d(
                        x=[current_pos['x']],
                        y=[current_pos['y']],
                        z=[current_pos['z']],
                        mode='markers',
                        marker=dict(
                            size=8,
                            color=self.color_palette['other'],
                            symbol='circle'
                        ),
                        name=f'{flight_id} @ {current_time}s',
                        showlegend=False
                    ))
        
        # Add conflict zones
        if conflict_results and conflict_results['conflicts']:
            self._add_conflict_zones_3d(fig, conflict_results['conflicts'], current_time)
        
        # Set 3D layout
        fig.update_layout(
            scene=dict(
                xaxis_title="X (meters)",
                yaxis_title="Y (meters)",
                zaxis_title="Z (meters)",
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.5)
                ),
                aspectmode='cube'
            )
        )
        
        return fig
    
    def _create_2d_plot(self, primary_trajectory: List[Dict], 
                       other_trajectories: List[Dict], 
                       conflict_results: Dict, 
                       current_time: float) -> go.Figure:
        """
        Create 2D top-down airspace visualization.
        """
        fig = go.Figure()
        
        # Add primary trajectory
        if primary_trajectory:
            primary_df = pd.DataFrame(primary_trajectory)
            
            fig.add_trace(go.Scatter(
                x=primary_df['x'],
                y=primary_df['y'],
                mode='lines+markers',
                line=dict(color=self.color_palette['primary'], width=4),
                marker=dict(size=6),
                name='Primary Mission',
                hovertemplate="<b>Primary Mission</b><br>" +
                            "Position: (%{x:.1f}, %{y:.1f})<br>" +
                            "Altitude: %{text:.1f}m<extra></extra>",
                text=primary_df['z']
            ))
            
            # Current position
            current_pos = self._get_position_at_time(primary_trajectory, current_time)
            if current_pos:
                fig.add_trace(go.Scatter(
                    x=[current_pos['x']],
                    y=[current_pos['y']],
                    mode='markers',
                    marker=dict(
                        size=15,
                        color=self.color_palette['primary'],
                        symbol='diamond'
                    ),
                    name=f'Primary @ {current_time}s',
                    showlegend=False
                ))
        
        # Add other trajectories
        for traj_data in enumerate(other_trajectories):
            trajectory = traj_data['trajectory']
            flight_id = traj_data['flight_id']
            
            if trajectory:
                traj_df = pd.DataFrame(trajectory)
                
                fig.add_trace(go.Scatter(
                    x=traj_df['x'],
                    y=traj_df['y'],
                    mode='lines+markers',
                    line=dict(color=self.color_palette['other'], width=3, dash='dot'),
                    marker=dict(size=4),
                    name=f'Flight {flight_id}',
                    hovertemplate=f"<b>Flight {flight_id}</b><br>" +
                                "Position: (%{x:.1f}, %{y:.1f})<br>" +
                                "Altitude: %{text:.1f}m<extra></extra>",
                    text=traj_df['z']
                ))
        
        # Add conflict zones (2D circles)
        if conflict_results and conflict_results['conflicts']:
            self._add_conflict_zones_2d(fig, conflict_results['conflicts'], current_time)
        
        # Set 2D layout
        fig.update_layout(
            xaxis_title="X (meters)",
            yaxis_title="Y (meters)",
            xaxis=dict(scaleanchor="y", scaleratio=1),
            yaxis=dict(scaleanchor="x", scaleratio=1)
        )
        
        return fig
    
    def _add_conflict_zones_3d(self, fig: go.Figure, conflicts: List[Dict], current_time: float):
        """
        Add 3D conflict zone visualizations.
        """
        for conflict in conflicts:
            # Only show conflicts relevant to current time
            if abs(conflict['time'] - current_time) <= 30:  # 30 second window
                center = conflict['location']
                radius = conflict['safety_buffer']
                
                # Create sphere points
                phi, theta = np.mgrid[0:np.pi:20j, 0:2*np.pi:20j]
                x_sphere = center['x'] + radius * np.sin(phi) * np.cos(theta)
                y_sphere = center['y'] + radius * np.sin(phi) * np.sin(theta)
                z_sphere = center['z'] + radius * np.cos(phi)
                
                # Add conflict zone as mesh
                fig.add_trace(go.Mesh3d(
                    x=x_sphere.flatten(),
                    y=y_sphere.flatten(),
                    z=z_sphere.flatten(),
                    alphahull=0,
                    opacity=0.3,
                    color=self.color_palette['conflict'],
                    name=f'Conflict Zone @ {conflict["time"]}s',
                    showlegend=False
                ))
    
    def _add_conflict_zones_2d(self, fig: go.Figure, conflicts: List[Dict], current_time: float):
        """
        Add 2D conflict zone visualizations as circles.
        """
        for conflict in conflicts:
            if abs(conflict['time'] - current_time) <= 30:
                center = conflict['location']
                radius = conflict['safety_buffer']
                
                # Create circle
                theta = np.linspace(0, 2*np.pi, 50)
                x_circle = center['x'] + radius * np.cos(theta)
                y_circle = center['y'] + radius * np.sin(theta)
                
                fig.add_trace(go.Scatter(
                    x=x_circle,
                    y=y_circle,
                    mode='lines',
                    line=dict(color=self.color_palette['conflict'], width=2, dash='dash'),
                    fill='toself',
                    fillcolor=f"rgba(214, 39, 40, 0.2)",
                    name=f'Conflict @ {conflict["time"]}s',
                    showlegend=False
                ))
    
    def _get_position_at_time(self, trajectory: List[Dict], target_time: float) -> Dict:
        """
        Get position at specific time from trajectory.
        """
        if not trajectory:
            return None
            
        # Find closest time point
        closest_point = min(trajectory, key=lambda p: abs(p['time'] - target_time))
        
        # Return position if within reasonable time range
        if abs(closest_point['time'] - target_time) <= 30:
            return closest_point
        
        return None
    
    def create_conflict_timeline(self, conflicts: List[Dict]) -> go.Figure:
        """
        Create timeline visualization of conflicts.
        """
        if not conflicts:
            return go.Figure()
        
        fig = go.Figure()
        
        times = [c['time'] for c in conflicts]
        severities = [c['severity_score'] for c in conflicts]
        flight_ids = [c['other_flight_id'] for c in conflicts]
        
        colors = [self.color_palette['conflict'] if s > 0.7 else 
                 self.color_palette['other'] if s > 0.4 else 
                 self.color_palette['safe'] for s in severities]
        
        fig.add_trace(go.Scatter(
            x=times,
            y=severities,
            mode='markers+lines',
            marker=dict(
                size=12,
                color=colors,
                line=dict(width=2, color='white')
            ),
            text=flight_ids,
            hovertemplate="<b>Conflict</b><br>" +
                        "Time: %{x}s<br>" +
                        "Severity: %{y:.2f}<br>" +
                        "Flight: %{text}<extra></extra>"
        ))
        
        fig.update_layout(
            title="Conflict Timeline",
            xaxis_title="Time (seconds)",
            yaxis_title="Conflict Severity",
            showlegend=False
        )
        
        return fig
