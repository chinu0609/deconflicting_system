import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from utils import calculate_distance_3d, interpolate_position

class DeconflictionEngine:
    """
    Core engine for UAV strategic deconfliction.
    Performs spatial and temporal conflict detection between drone trajectories.
    """
    
    def __init__(self):
        self.conflict_types = {
            'spatial': 'Spatial proximity conflict',
            'temporal': 'Temporal overlap conflict',
            'trajectory': 'Trajectory intersection conflict'
        }
    
    def check_conflicts(self, primary_trajectory: List[Dict], other_trajectories: List[Dict], 
                       safety_buffer: float = 50.0) -> Dict[str, Any]:
        """
        Main conflict detection method.
        
        Args:
            primary_trajectory: List of trajectory points for primary drone
            other_trajectories: List of trajectory data for other drones
            safety_buffer: Minimum safe distance in meters
            
        Returns:
            Dictionary containing conflict analysis results
        """
        conflicts = []
        analysis_summary = {
            'total_checks': 0,
            'spatial_violations': 0,
            'temporal_violations': 0,
            'safe_segments': 0
        }
        
        for other_traj_data in other_trajectories:
            other_trajectory = other_traj_data['trajectory']
            other_flight_id = other_traj_data['flight_id']
            
            # Perform pairwise conflict detection
            traj_conflicts = self._detect_trajectory_conflicts(
                primary_trajectory,
                other_trajectory,
                other_flight_id,
                safety_buffer
            )
            
            conflicts.extend(traj_conflicts)
            analysis_summary['total_checks'] += len(primary_trajectory) * len(other_trajectory)
        
        # Classify conflicts
        for conflict in conflicts:
            if conflict['type'] == 'spatial':
                analysis_summary['spatial_violations'] += 1
            elif conflict['type'] == 'temporal':
                analysis_summary['temporal_violations'] += 1
        
        # Sort conflicts by severity and time
        conflicts.sort(key=lambda x: (x['severity_score'], x['time']))
        
        return {
            'conflicts': conflicts,
            'summary': analysis_summary,
            'is_safe': len(conflicts) == 0,
            'total_conflicts': len(conflicts)
        }
    
    def _detect_trajectory_conflicts(self, primary_traj: List[Dict], other_traj: List[Dict],
                                   other_flight_id: str, safety_buffer: float) -> List[Dict]:
        """
        Detect conflicts between two specific trajectories.
        """
        conflicts = []
        
        # Create time-indexed lookups for efficient checking
        primary_by_time = {point['time']: point for point in primary_traj}
        other_by_time = {point['time']: point for point in other_traj}
        
        # Get all unique time points
        all_times = sorted(set(primary_by_time.keys()) | set(other_by_time.keys()))
        
        for time_point in all_times:
            # Get positions at this time (interpolate if necessary)
            primary_pos = self._get_position_at_time(primary_traj, time_point)
            other_pos = self._get_position_at_time(other_traj, time_point)
            
            if primary_pos and other_pos:
                distance = calculate_distance_3d(primary_pos, other_pos)
                
                if distance < safety_buffer:
                    conflict = self._create_conflict_record(
                        primary_pos, other_pos, time_point, distance,
                        other_flight_id, safety_buffer
                    )
                    conflicts.append(conflict)
        
        return conflicts
    
    def _get_position_at_time(self, trajectory: List[Dict], target_time: float) -> Dict:
        """
        Get drone position at specific time, interpolating if necessary.
        """
        # Find exact match first
        for point in trajectory:
            if point['time'] == target_time:
                return point
        
        # Find surrounding points for interpolation
        before_point = None
        after_point = None
        
        for point in trajectory:
            if point['time'] < target_time:
                if not before_point or point['time'] > before_point['time']:
                    before_point = point
            elif point['time'] > target_time:
                if not after_point or point['time'] < after_point['time']:
                    after_point = point
        
        # Interpolate position
        if before_point and after_point:
            return interpolate_position(before_point, after_point, target_time)
        elif before_point:
            return before_point
        elif after_point:
            return after_point
        
        return None
    
    def _create_conflict_record(self, primary_pos: Dict, other_pos: Dict, time_point: float,
                              distance: float, other_flight_id: str, safety_buffer: float) -> Dict:
        """
        Create a detailed conflict record.
        """
        severity_score = max(0, (safety_buffer - distance) / safety_buffer)
        
        # Determine conflict type
        conflict_type = 'spatial'
        description = f"Drones within {distance:.1f}m at time {time_point}s"
        
        if distance < safety_buffer * 0.5:
            severity = 'HIGH'
        elif distance < safety_buffer * 0.8:
            severity = 'MEDIUM'
        else:
            severity = 'LOW'
        
        return {
            'type': conflict_type,
            'time': time_point,
            'location': {
                'x': (primary_pos['x'] + other_pos['x']) / 2,
                'y': (primary_pos['y'] + other_pos['y']) / 2,
                'z': (primary_pos['z'] + other_pos['z']) / 2
            },
            'distance': distance,
            'safety_buffer': safety_buffer,
            'severity': severity,
            'severity_score': severity_score,
            'other_flight_id': other_flight_id,
            'description': description,
            'primary_position': primary_pos,
            'other_position': other_pos
        }
    
    def get_conflict_zones(self, conflicts: List[Dict], buffer_expansion: float = 1.5) -> List[Dict]:
        """
        Generate conflict zone boundaries for visualization.
        """
        zones = []
        
        for conflict in conflicts:
            zone = {
                'center': conflict['location'],
                'radius': conflict['safety_buffer'] * buffer_expansion,
                'severity': conflict['severity'],
                'time_start': max(0, conflict['time'] - 10),
                'time_end': conflict['time'] + 10,
                'conflict_id': f"{conflict['other_flight_id']}_{conflict['time']}"
            }
            zones.append(zone)
        
        return zones
    
    def suggest_resolution(self, conflicts: List[Dict]) -> List[Dict]:
        """
        Suggest resolution strategies for detected conflicts.
        """
        suggestions = []
        
        for conflict in conflicts:
            if conflict['severity'] == 'HIGH':
                suggestion = {
                    'type': 'altitude_change',
                    'description': 'Recommend altitude separation of ±25m',
                    'priority': 'immediate'
                }
            elif conflict['severity'] == 'MEDIUM':
                suggestion = {
                    'type': 'time_shift',
                    'description': 'Delay mission start by 30-60 seconds',
                    'priority': 'high'
                }
            else:
                suggestion = {
                    'type': 'route_adjustment',
                    'description': 'Minor route adjustment to increase separation',
                    'priority': 'normal'
                }
            
            suggestion['conflict_time'] = conflict['time']
            suggestion['affected_flight'] = conflict['other_flight_id']
            suggestions.append(suggestion)
        
        return suggestions
