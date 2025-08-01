import math
import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta

def calculate_distance_3d(pos1: Dict, pos2: Dict) -> float:
    """
    Calculate 3D Euclidean distance between two positions.
    
    Args:
        pos1: Dictionary with x, y, z coordinates
        pos2: Dictionary with x, y, z coordinates
        
    Returns:
        Distance in meters
    """
    dx = pos1['x'] - pos2['x']
    dy = pos1['y'] - pos2['y']
    dz = pos1['z'] - pos2['z']
    
    return math.sqrt(dx*dx + dy*dy + dz*dz)

def calculate_distance_2d(pos1: Dict, pos2: Dict) -> float:
    """
    Calculate 2D distance between two positions (ignoring altitude).
    """
    dx = pos1['x'] - pos2['x']
    dy = pos1['y'] - pos2['y']
    
    return math.sqrt(dx*dx + dy*dy)

def interpolate_position(pos1: Dict, pos2: Dict, target_time: float) -> Dict:
    """
    Linearly interpolate position between two waypoints at target time.
    
    Args:
        pos1: Earlier position with time
        pos2: Later position with time
        target_time: Time for interpolated position
        
    Returns:
        Interpolated position dictionary
    """
    if pos1['time'] == pos2['time']:
        return pos1
    
    # Calculate interpolation ratio
    time_ratio = (target_time - pos1['time']) / (pos2['time'] - pos1['time'])
    time_ratio = max(0, min(1, time_ratio))  # Clamp between 0 and 1
    
    return {
        'x': pos1['x'] + time_ratio * (pos2['x'] - pos1['x']),
        'y': pos1['y'] + time_ratio * (pos2['y'] - pos1['y']),
        'z': pos1['z'] + time_ratio * (pos2['z'] - pos1['z']),
        'time': target_time
    }

def validate_waypoints(waypoints: List[Dict]) -> bool:
    """
    Validate waypoint data structure and values.
    
    Args:
        waypoints: List of waypoint dictionaries
        
    Returns:
        True if valid, False otherwise
    """
    if not waypoints or len(waypoints) < 2:
        return False
    
    required_fields = ['x', 'y', 'z']
    
    for wp in waypoints:
        # Check required fields
        if not all(field in wp for field in required_fields):
            return False
        
        # Check data types and reasonable ranges
        try:
            x, y, z = float(wp['x']), float(wp['y']), float(wp['z'])
            
            # Basic range validation
            if abs(x) > 10000 or abs(y) > 10000:  # Reasonable coordinate limits
                return False
            if z < 0 or z > 1000:  # Altitude limits
                return False
                
        except (ValueError, TypeError):
            return False
    
    return True

def format_time(seconds: float) -> str:
    """
    Format time in seconds to human-readable string.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted time string
    """
    if seconds < 0:
        return f"-{format_time(-seconds)}"
    
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    
    if minutes > 0:
        return f"{minutes}m {remaining_seconds}s"
    else:
        return f"{remaining_seconds}s"

def calculate_bearing(pos1: Dict, pos2: Dict) -> float:
    """
    Calculate bearing (direction) from pos1 to pos2 in degrees.
    
    Args:
        pos1: Starting position
        pos2: End position
        
    Returns:
        Bearing in degrees (0-360)
    """
    dx = pos2['x'] - pos1['x']
    dy = pos2['y'] - pos1['y']
    
    bearing = math.atan2(dy, dx) * 180 / math.pi
    
    # Convert to 0-360 range
    return (bearing + 360) % 360

def calculate_flight_metrics(trajectory: List[Dict]) -> Dict[str, Any]:
    """
    Calculate various metrics for a flight trajectory.
    
    Args:
        trajectory: List of trajectory points
        
    Returns:
        Dictionary with calculated metrics
    """
    if not trajectory or len(trajectory) < 2:
        return {}
    
    total_distance = 0.0
    max_speed = 0.0
    min_altitude = float('inf')
    max_altitude = float('-inf')
    
    for i in range(len(trajectory) - 1):
        p1, p2 = trajectory[i], trajectory[i + 1]
        
        # Distance calculation
        segment_distance = calculate_distance_3d(p1, p2)
        total_distance += segment_distance
        
        # Speed calculation
        time_diff = p2['time'] - p1['time']
        if time_diff > 0:
            speed = segment_distance / time_diff
            max_speed = max(max_speed, speed)
        
        # Altitude tracking
        min_altitude = min(min_altitude, p1['z'])
        max_altitude = max(max_altitude, p1['z'])
    
    # Include last point altitude
    if trajectory:
        min_altitude = min(min_altitude, trajectory[-1]['z'])
        max_altitude = max(max_altitude, trajectory[-1]['z'])
    
    duration = trajectory[-1]['time'] - trajectory[0]['time']
    avg_speed = total_distance / duration if duration > 0 else 0
    
    return {
        'total_distance': total_distance,
        'duration': duration,
        'average_speed': avg_speed,
        'max_speed': max_speed,
        'min_altitude': min_altitude,
        'max_altitude': max_altitude,
        'altitude_range': max_altitude - min_altitude,
        'total_waypoints': len(trajectory)
    }

def generate_safety_buffer_recommendations(conflicts: List[Dict]) -> List[Dict]:
    """
    Generate recommendations for safety buffer adjustments based on conflicts.
    
    Args:
        conflicts: List of detected conflicts
        
    Returns:
        List of recommendation dictionaries
    """
    recommendations = []
    
    if not conflicts:
        recommendations.append({
            'type': 'maintain',
            'message': 'Current safety buffer is adequate',
            'suggested_buffer': None
        })
        return recommendations
    
    # Analyze conflict distances
    min_distance = min(c['distance'] for c in conflicts)
    avg_distance = sum(c['distance'] for c in conflicts) / len(conflicts)
    
    # High severity conflicts
    high_severity_conflicts = [c for c in conflicts if c['severity'] == 'HIGH']
    if high_severity_conflicts:
        recommended_buffer = min_distance * 2.5
        recommendations.append({
            'type': 'increase',
            'message': f'High severity conflicts detected. Recommend increasing safety buffer to {recommended_buffer:.1f}m',
            'suggested_buffer': recommended_buffer,
            'reason': 'Critical proximity violations'
        })
    
    # Multiple conflicts
    if len(conflicts) > 3:
        recommendations.append({
            'type': 'temporal_adjustment',
            'message': 'Multiple conflicts detected. Consider temporal separation or route modification',
            'suggested_buffer': None,
            'reason': 'High conflict density'
        })
    
    return recommendations

def export_mission_data(scenario: Dict, conflict_results: Dict, 
                       parameters: Dict) -> Dict[str, Any]:
    """
    Export complete mission data for analysis or reporting.
    
    Args:
        scenario: Mission scenario data
        conflict_results: Conflict analysis results
        parameters: Analysis parameters
        
    Returns:
        Complete export data structure
    """
    export_data = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'scenario_type': scenario.get('type', 'unknown'),
            'analysis_version': '1.0'
        },
        'mission': {
            'primary_waypoints': scenario['primary_mission']['waypoints'],
            'start_time': scenario['primary_mission']['start_time'],
            'end_time': scenario['primary_mission']['end_time'],
            'duration': scenario['mission_duration']
        },
        'other_flights': scenario['other_flights'],
        'analysis': {
            'parameters': parameters,
            'conflicts': conflict_results.get('conflicts', []),
            'summary': conflict_results.get('summary', {}),
            'is_safe': conflict_results.get('is_safe', False)
        },
        'recommendations': generate_safety_buffer_recommendations(
            conflict_results.get('conflicts', [])
        )
    }
    
    return export_data

def validate_mission_timing(primary_mission: Dict, other_flights: List[Dict]) -> List[str]:
    """
    Validate timing constraints across all missions.
    
    Args:
        primary_mission: Primary mission data
        other_flights: List of other flight missions
        
    Returns:
        List of validation warnings/errors
    """
    warnings = []
    
    # Check primary mission timing
    if primary_mission['start_time'] >= primary_mission['end_time']:
        warnings.append("Primary mission start time must be before end time")
    
    # Check for reasonable mission duration
    duration = primary_mission['end_time'] - primary_mission['start_time']
    if duration < 60:
        warnings.append("Primary mission duration is very short (< 1 minute)")
    elif duration > 3600:
        warnings.append("Primary mission duration is very long (> 1 hour)")
    
    # Check other flights
    for flight in other_flights:
        if flight['start_time'] >= flight['end_time']:
            warnings.append(f"Flight {flight['flight_id']} has invalid timing")
        
        # Check for overlapping operational windows
        if (flight['start_time'] < primary_mission['end_time'] and 
            flight['end_time'] > primary_mission['start_time']):
            # This is actually expected for conflict detection, not a warning
            pass
    
    return warnings
