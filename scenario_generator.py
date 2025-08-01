import numpy as np
import random
from typing import List, Dict, Any
from datetime import datetime, timedelta

class ScenarioGenerator:
    """
    Generates various UAV mission scenarios for testing the deconfliction system.
    Creates realistic flight patterns with different conflict types.
    """
    
    def __init__(self):
        self.airspace_bounds = {
            'x_min': -200, 'x_max': 200,
            'y_min': -200, 'y_max': 200,
            'z_min': 30, 'z_max': 120
        }
        self.default_mission_duration = 300  # 5 minutes
        
    def generate_scenario(self, scenario_type: str) -> Dict[str, Any]:
        """
        Generate a complete scenario with primary mission and other flights.
        """
        scenarios = {
            'conflict_free': self._generate_conflict_free_scenario,
            'spatial_conflict': self._generate_spatial_conflict_scenario,
            'temporal_conflict': self._generate_temporal_conflict_scenario,
            'complex_scenario': self._generate_complex_scenario,
            'altitude_conflict': self._generate_altitude_conflict_scenario
        }
        
        if scenario_type in scenarios:
            return scenarios[scenario_type]()
        else:
            return self._generate_conflict_free_scenario()
    
    def create_custom_scenario(self, waypoints: List[Dict], start_time: float, 
                             end_time: float) -> Dict[str, Any]:
        """
        Create a custom scenario from user-provided waypoints.
        """
        # Generate some background traffic
        other_flights = self._generate_background_traffic(3)
        
        return {
            'type': 'custom',
            'primary_mission': {
                'waypoints': waypoints,
                'start_time': start_time,
                'end_time': end_time
            },
            'other_flights': other_flights,
            'mission_duration': end_time - start_time,
            'description': 'Custom user-defined mission'
        }
    
    def _generate_conflict_free_scenario(self) -> Dict[str, Any]:
        """
        Generate a scenario with no conflicts - well-separated trajectories.
        """
        # Primary mission: simple rectangular pattern
        primary_waypoints = [
            {'x': 0, 'y': 0, 'z': 60, 'time': 0},
            {'x': 80, 'y': 0, 'z': 60, 'time': 60},
            {'x': 80, 'y': 80, 'z': 70, 'time': 120},
            {'x': 0, 'y': 80, 'z': 70, 'time': 180},
            {'x': 0, 'y': 0, 'z': 60, 'time': 240}
        ]
        
        # Other flights with good separation
        other_flights = [
            {
                'flight_id': 'UAV_002',
                'waypoints': [
                    {'x': -100, 'y': -50, 'z': 45, 'time': 0},
                    {'x': -100, 'y': 50, 'z': 45, 'time': 100},
                    {'x': -150, 'y': 50, 'z': 50, 'time': 200}
                ],
                'start_time': 30,
                'end_time': 230
            },
            {
                'flight_id': 'UAV_003',
                'waypoints': [
                    {'x': 150, 'y': 100, 'z': 90, 'time': 0},
                    {'x': 120, 'y': 150, 'z': 90, 'time': 80},
                    {'x': 180, 'y': 150, 'z': 85, 'time': 160}
                ],
                'start_time': 60,
                'end_time': 220
            }
        ]
        
        return {
            'type': 'conflict_free',
            'primary_mission': {
                'waypoints': primary_waypoints,
                'start_time': 0,
                'end_time': 240
            },
            'other_flights': other_flights,
            'mission_duration': 240,
            'description': 'Well-separated trajectories with no conflicts'
        }
    
    def _generate_spatial_conflict_scenario(self) -> Dict[str, Any]:
        """
        Generate a scenario with spatial conflicts - trajectories cross paths.
        """
        # Primary mission: diagonal crossing
        primary_waypoints = [
            {'x': -50, 'y': -50, 'z': 60, 'time': 0},
            {'x': 0, 'y': 0, 'z': 60, 'time': 60},
            {'x': 50, 'y': 50, 'z': 60, 'time': 120},
            {'x': 100, 'y': 100, 'z': 65, 'time': 180}
        ]
        
        # Conflicting flight crossing the primary path
        other_flights = [
            {
                'flight_id': 'UAV_CONFLICT',
                'waypoints': [
                    {'x': 50, 'y': -50, 'z': 55, 'time': 0},
                    {'x': 0, 'y': 0, 'z': 55, 'time': 60},
                    {'x': -50, 'y': 50, 'z': 55, 'time': 120}
                ],
                'start_time': 20,
                'end_time': 140
            },
            {
                'flight_id': 'UAV_SAFE',
                'waypoints': [
                    {'x': -100, 'y': 100, 'z': 80, 'time': 0},
                    {'x': -80, 'y': 120, 'z': 80, 'time': 100}
                ],
                'start_time': 0,
                'end_time': 100
            }
        ]
        
        return {
            'type': 'spatial_conflict',
            'primary_mission': {
                'waypoints': primary_waypoints,
                'start_time': 0,
                'end_time': 180
            },
            'other_flights': other_flights,
            'mission_duration': 180,
            'description': 'Trajectories crossing with spatial conflicts'
        }
    
    def _generate_temporal_conflict_scenario(self) -> Dict[str, Any]:
        """
        Generate a scenario with temporal conflicts - same space, different times.
        """
        # Primary mission using a common corridor
        primary_waypoints = [
            {'x': 0, 'y': 0, 'z': 50, 'time': 0},
            {'x': 40, 'y': 40, 'z': 50, 'time': 60},
            {'x': 80, 'y': 80, 'z': 55, 'time': 120},
            {'x': 120, 'y': 120, 'z': 55, 'time': 180}
        ]
        
        # Other flight using same corridor but earlier
        other_flights = [
            {
                'flight_id': 'UAV_EARLIER',
                'waypoints': [
                    {'x': 120, 'y': 120, 'z': 45, 'time': 0},
                    {'x': 80, 'y': 80, 'z': 45, 'time': 60},
                    {'x': 40, 'y': 40, 'z': 50, 'time': 120},
                    {'x': 0, 'y': 0, 'z': 50, 'time': 180}
                ],
                'start_time': -60,  # Starts earlier
                'end_time': 120
            },
            {
                'flight_id': 'UAV_OVERLAP',
                'waypoints': [
                    {'x': 20, 'y': 20, 'z': 48, 'time': 0},
                    {'x': 60, 'y': 60, 'z': 48, 'time': 80},
                    {'x': 100, 'y': 100, 'z': 52, 'time': 160}
                ],
                'start_time': 40,  # Overlaps with primary
                'end_time': 200
            }
        ]
        
        return {
            'type': 'temporal_conflict',
            'primary_mission': {
                'waypoints': primary_waypoints,
                'start_time': 0,
                'end_time': 180
            },
            'other_flights': other_flights,
            'mission_duration': 180,
            'description': 'Temporal overlaps in shared corridor usage'
        }
    
    def _generate_altitude_conflict_scenario(self) -> Dict[str, Any]:
        """
        Generate a scenario with altitude-based conflicts.
        """
        # Primary mission at medium altitude
        primary_waypoints = [
            {'x': 0, 'y': 0, 'z': 60, 'time': 0},
            {'x': 50, 'y': 30, 'z': 65, 'time': 80},
            {'x': 100, 'y': 0, 'z': 70, 'time': 160},
            {'x': 100, 'y': -30, 'z': 65, 'time': 240}
        ]
        
        # Conflicting flights at similar altitudes
        other_flights = [
            {
                'flight_id': 'UAV_LOW',
                'waypoints': [
                    {'x': 20, 'y': 10, 'z': 55, 'time': 0},
                    {'x': 70, 'y': 20, 'z': 60, 'time': 100},
                    {'x': 90, 'y': 10, 'z': 65, 'time': 180}
                ],
                'start_time': 30,
                'end_time': 210
            },
            {
                'flight_id': 'UAV_HIGH',
                'waypoints': [
                    {'x': 10, 'y': -10, 'z': 75, 'time': 0},
                    {'x': 60, 'y': 0, 'z': 70, 'time': 120},
                    {'x': 110, 'y': -20, 'z': 68, 'time': 200}
                ],
                'start_time': 60,
                'end_time': 260
            }
        ]
        
        return {
            'type': 'altitude_conflict',
            'primary_mission': {
                'waypoints': primary_waypoints,
                'start_time': 0,
                'end_time': 240
            },
            'other_flights': other_flights,
            'mission_duration': 240,
            'description': 'Altitude separation conflicts in 3D space'
        }
    
    def _generate_complex_scenario(self) -> Dict[str, Any]:
        """
        Generate a complex scenario with multiple types of conflicts.
        """
        # Primary mission: complex pattern
        primary_waypoints = [
            {'x': 0, 'y': 0, 'z': 50, 'time': 0},
            {'x': 60, 'y': 40, 'z': 60, 'time': 80},
            {'x': 40, 'y': 80, 'z': 70, 'time': 160},
            {'x': -20, 'y': 60, 'z': 65, 'time': 240},
            {'x': -40, 'y': 20, 'z': 55, 'time': 320},
            {'x': 0, 'y': 0, 'z': 50, 'time': 400}
        ]
        
        # Multiple conflicting flights
        other_flights = [
            {
                'flight_id': 'UAV_ALPHA',
                'waypoints': [
                    {'x': 80, 'y': 20, 'z': 45, 'time': 0},
                    {'x': 20, 'y': 60, 'z': 55, 'time': 120},
                    {'x': -30, 'y': 40, 'z': 60, 'time': 200}
                ],
                'start_time': 50,
                'end_time': 250
            },
            {
                'flight_id': 'UAV_BETA',
                'waypoints': [
                    {'x': -60, 'y': -20, 'z': 80, 'time': 0},
                    {'x': 0, 'y': 40, 'z': 75, 'time': 150},
                    {'x': 60, 'y': 80, 'z': 70, 'time': 300}
                ],
                'start_time': 100,
                'end_time': 400
            },
            {
                'flight_id': 'UAV_GAMMA',
                'waypoints': [
                    {'x': 40, 'y': -40, 'z': 35, 'time': 0},
                    {'x': 0, 'y': 0, 'z': 45, 'time': 80},
                    {'x': -40, 'y': 40, 'z': 50, 'time': 160}
                ],
                'start_time': 0,
                'end_time': 160
            }
        ]
        
        return {
            'type': 'complex_scenario',
            'primary_mission': {
                'waypoints': primary_waypoints,
                'start_time': 0,
                'end_time': 400
            },
            'other_flights': other_flights,
            'mission_duration': 400,
            'description': 'Complex multi-drone scenario with various conflict types'
        }
    
    def _generate_background_traffic(self, num_flights: int) -> List[Dict]:
        """
        Generate random background traffic for custom scenarios.
        """
        flights = []
        
        for i in range(num_flights):
            # Random waypoints within airspace
            num_waypoints = random.randint(3, 6)
            waypoints = []
            
            for j in range(num_waypoints):
                waypoint = {
                    'x': random.uniform(self.airspace_bounds['x_min'], self.airspace_bounds['x_max']),
                    'y': random.uniform(self.airspace_bounds['y_min'], self.airspace_bounds['y_max']),
                    'z': random.uniform(self.airspace_bounds['z_min'], self.airspace_bounds['z_max']),
                    'time': j * random.uniform(60, 120)
                }
                waypoints.append(waypoint)
            
            flight = {
                'flight_id': f'BG_{i+1:03d}',
                'waypoints': waypoints,
                'start_time': random.uniform(-60, 120),
                'end_time': waypoints[-1]['time'] + random.uniform(30, 90)
            }
            
            flights.append(flight)
        
        return flights
    
    def get_scenario_descriptions(self) -> Dict[str, str]:
        """
        Get descriptions of all available scenarios.
        """
        return {
            'conflict_free': 'Well-separated trajectories with no conflicts',
            'spatial_conflict': 'Trajectories crossing with spatial conflicts',
            'temporal_conflict': 'Temporal overlaps in shared corridor usage',
            'complex_scenario': 'Complex multi-drone scenario with various conflict types',
            'altitude_conflict': 'Altitude separation conflicts in 3D space'
        }
