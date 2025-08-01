import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import math

class TrajectoryCalculator:
    """
    Calculates detailed drone trajectories from waypoint missions.
    Handles interpolation, speed calculations, and temporal positioning.
    """
    
    def __init__(self):
        self.default_speed = 15.0  # m/s
        self.max_speed = 30.0      # m/s
        self.min_speed = 5.0       # m/s
    
    def calculate_trajectory(self, waypoints: List[Dict], start_time: float, 
                           end_time: float, time_step: int = 5) -> List[Dict]:
        """
        Calculate complete trajectory from waypoints with temporal information.
        
        Args:
            waypoints: List of waypoint dictionaries with x, y, z, time
            start_time: Mission start time in seconds
            end_time: Mission end time in seconds
            time_step: Time discretization step in seconds
            
        Returns:
            List of trajectory points with positions and timing
        """
        if not waypoints or len(waypoints) < 2:
            return []
        
        # Normalize waypoint times to mission window
        normalized_waypoints = self._normalize_waypoint_times(waypoints, start_time, end_time)
        
        # Generate trajectory points
        trajectory_points = []
        current_time = start_time
        
        while current_time <= end_time:
            position = self._interpolate_position_at_time(normalized_waypoints, current_time)
            if position:
                trajectory_point = {
                    'time': current_time,
                    'x': position['x'],
                    'y': position['y'],
                    'z': position['z'],
                    'speed': self._calculate_speed_at_time(normalized_waypoints, current_time),
                    'heading': self._calculate_heading_at_time(normalized_waypoints, current_time)
                }
                trajectory_points.append(trajectory_point)
            
            current_time += time_step
        
        # Ensure end waypoint is included
        if trajectory_points and trajectory_points[-1]['time'] < end_time:
            final_position = normalized_waypoints[-1]
            trajectory_points.append({
                'time': end_time,
                'x': final_position['x'],
                'y': final_position['y'],
                'z': final_position['z'],
                'speed': 0.0,
                'heading': trajectory_points[-1]['heading'] if trajectory_points else 0.0
            })
        
        return trajectory_points
    
    def _normalize_waypoint_times(self, waypoints: List[Dict], start_time: float, 
                                end_time: float) -> List[Dict]:
        """
        Normalize waypoint times to fit within mission time window.
        """
        if not waypoints:
            return []
        
        normalized = []
        mission_duration = end_time - start_time
        
        # If waypoints have explicit times, use them
        if all('time' in wp for wp in waypoints):
            for wp in waypoints:
                normalized_time = start_time + (wp['time'] / max(wp['time'] for wp in waypoints)) * mission_duration
                normalized.append({
                    'x': wp['x'],
                    'y': wp['y'],
                    'z': wp.get('z', 50.0),
                    'time': normalized_time
                })
        else:
            # Distribute waypoints evenly across mission duration
            for i, wp in enumerate(waypoints):
                time_fraction = i / (len(waypoints) - 1) if len(waypoints) > 1 else 0
                normalized_time = start_time + time_fraction * mission_duration
                normalized.append({
                    'x': wp['x'],
                    'y': wp['y'],
                    'z': wp.get('z', 50.0),
                    'time': normalized_time
                })
        
        return sorted(normalized, key=lambda x: x['time'])
    
    def _interpolate_position_at_time(self, waypoints: List[Dict], target_time: float) -> Dict:
        """
        Interpolate drone position at specific time using waypoints.
        """
        if not waypoints:
            return None
        
        # Handle edge cases
        if target_time <= waypoints[0]['time']:
            return waypoints[0]
        if target_time >= waypoints[-1]['time']:
            return waypoints[-1]
        
        # Find surrounding waypoints
        for i in range(len(waypoints) - 1):
            wp1, wp2 = waypoints[i], waypoints[i + 1]
            
            if wp1['time'] <= target_time <= wp2['time']:
                # Linear interpolation
                time_ratio = (target_time - wp1['time']) / (wp2['time'] - wp1['time'])
                
                return {
                    'x': wp1['x'] + time_ratio * (wp2['x'] - wp1['x']),
                    'y': wp1['y'] + time_ratio * (wp2['y'] - wp1['y']),
                    'z': wp1['z'] + time_ratio * (wp2['z'] - wp1['z']),
                    'time': target_time
                }
        
        return waypoints[-1]
    
    def _calculate_speed_at_time(self, waypoints: List[Dict], target_time: float) -> float:
        """
        Calculate drone speed at specific time.
        """
        if len(waypoints) < 2:
            return 0.0
        
        # Find current segment
        for i in range(len(waypoints) - 1):
            wp1, wp2 = waypoints[i], waypoints[i + 1]
            
            if wp1['time'] <= target_time <= wp2['time']:
                distance = math.sqrt(
                    (wp2['x'] - wp1['x'])**2 + 
                    (wp2['y'] - wp1['y'])**2 + 
                    (wp2['z'] - wp1['z'])**2
                )
                time_diff = wp2['time'] - wp1['time']
                
                if time_diff > 0:
                    speed = distance / time_diff
                    return max(self.min_speed, min(self.max_speed, speed))
        
        return self.default_speed
    
    def _calculate_heading_at_time(self, waypoints: List[Dict], target_time: float) -> float:
        """
        Calculate drone heading (direction of travel) at specific time.
        """
        if len(waypoints) < 2:
            return 0.0
        
        # Find current segment
        for i in range(len(waypoints) - 1):
            wp1, wp2 = waypoints[i], waypoints[i + 1]
            
            if wp1['time'] <= target_time <= wp2['time']:
                dx = wp2['x'] - wp1['x']
                dy = wp2['y'] - wp1['y']
                
                heading = math.atan2(dy, dx) * 180 / math.pi
                return heading
        
        return 0.0
    
    def calculate_trajectory_metrics(self, trajectory: List[Dict]) -> Dict:
        """
        Calculate various metrics for a trajectory.
        """
        if not trajectory:
            return {}
        
        total_distance = 0.0
        max_speed = 0.0
        avg_altitude = 0.0
        
        for i in range(len(trajectory) - 1):
            p1, p2 = trajectory[i], trajectory[i + 1]
            segment_distance = math.sqrt(
                (p2['x'] - p1['x'])**2 + 
                (p2['y'] - p1['y'])**2 + 
                (p2['z'] - p1['z'])**2
            )
            total_distance += segment_distance
            max_speed = max(max_speed, p1.get('speed', 0))
        
        avg_altitude = sum(p['z'] for p in trajectory) / len(trajectory)
        
        return {
            'total_distance': total_distance,
            'max_speed': max_speed,
            'average_altitude': avg_altitude,
            'duration': trajectory[-1]['time'] - trajectory[0]['time'],
            'total_points': len(trajectory)
        }
    
    def smooth_trajectory(self, trajectory: List[Dict], smoothing_factor: float = 0.1) -> List[Dict]:
        """
        Apply smoothing to trajectory to reduce sharp turns.
        """
        if len(trajectory) < 3:
            return trajectory
        
        smoothed = [trajectory[0]]  # Keep first point unchanged
        
        for i in range(1, len(trajectory) - 1):
            prev_point = trajectory[i - 1]
            curr_point = trajectory[i]
            next_point = trajectory[i + 1]
            
            # Apply exponential smoothing
            smoothed_x = curr_point['x'] + smoothing_factor * (
                (prev_point['x'] + next_point['x']) / 2 - curr_point['x']
            )
            smoothed_y = curr_point['y'] + smoothing_factor * (
                (prev_point['y'] + next_point['y']) / 2 - curr_point['y']
            )
            smoothed_z = curr_point['z'] + smoothing_factor * (
                (prev_point['z'] + next_point['z']) / 2 - curr_point['z']
            )
            
            smoothed_point = curr_point.copy()
            smoothed_point.update({
                'x': smoothed_x,
                'y': smoothed_y,
                'z': smoothed_z
            })
            
            smoothed.append(smoothed_point)
        
        smoothed.append(trajectory[-1])  # Keep last point unchanged
        return smoothed
