"""
RightHandParser.py - Right hand trajectory generation for plucking motors

Handles right-hand plucking trajectories with dynamic range control.
Reusable class for any plucking operations in the system.

Motor Layout (Right Hand - Last 3 motors of 15-motor array):
- Motors 12-14: Picker motors (pluck strings with variable velocity/dynamics)

Features:
- MIDI velocity to pluck depth mapping
- State-based plucking (alternates between up/down)
- Smooth trajectory generation using interp_with_blend
- Integration with tune.py calibration values
"""

import numpy as np
import copy
from GuitarBotParser import GuitarBotParser  # Import for reusing interp_with_blend
import tune as tu
import plotly.graph_objects as go


class RightHandParser:
    def __init__(self):
        # Track current state of each picker motor (0=down, 1=up)
        # Mimics GuitarBotParser picker state logic
        self.picker_states = {0: 1, 1: 1, 2: 1}  # Start in up position
        
        # Motor position mappings from tune.py - convert mm to encoder ticks
        self.motor_info = {}
        for picker_id in range(len(tu.PICKER_MOTOR_INFO)):
            if picker_id in tu.PICKER_MOTOR_INFO:
                down_mm = tu.PICKER_MOTOR_INFO[picker_id]['down_pluck_mm']
                up_mm = tu.PICKER_MOTOR_INFO[picker_id]['up_pluck_mm']
                resolution = tu.PICKER_MOTOR_INFO[picker_id]['resolution']
                
                # Convert mm to encoder ticks using same formula as GuitarBotParser
                down_ticks = (down_mm * resolution) / tu.MM_TO_ENCODER_CONVERSION_FACTOR
                up_ticks = (up_mm * resolution) / tu.MM_TO_ENCODER_CONVERSION_FACTOR
                
                self.motor_info[picker_id] = {
                    'down_ticks': round(down_ticks, 3),
                    'up_ticks': round(up_ticks, 3),
                    'down_mm': down_mm,
                    'up_mm': up_mm,
                    'resolution': resolution
                }
        
        # Current positions in encoder ticks (start at up positions)
        self.current_positions = {}
        for picker_id in self.motor_info:
            self.current_positions[picker_id] = self.motor_info[picker_id]['up_ticks']
    
    def midi_note_to_picker_id(self, midi_note):
        """
        Convert MIDI note number to picker motor ID using STRING_MIDI_RANGES.
        
        Args:
            midi_note: MIDI note number
            
        Returns:
            Picker motor ID (0, 1, 2) or None if not supported
        """
        for picker_id, (low_note, high_note, direction) in enumerate(tu.STRING_MIDI_RANGES):
            if low_note <= midi_note <= high_note:
                return picker_id
        
        return None  # Note not supported by available pickers
    
    def velocity_to_position(self, picker_id, velocity):
        """
        Convert MIDI velocity to pluck position.
        
        Args:
            picker_id: Picker motor ID (0, 1, 2)
            velocity: MIDI velocity (0-127)
            
        Returns:
            Target position in encoder ticks
        """
        if picker_id not in self.motor_info:
            return None
        
        # Convert velocity to depth ratio (0-127 -> 0.0-1.0)
        velocity_ratio = velocity / 127.0
        
        # Calculate position between up and down limits
        up_ticks = self.motor_info[picker_id]['up_ticks']
        down_ticks = self.motor_info[picker_id]['down_ticks']
        
        target_ticks = up_ticks + velocity_ratio * (down_ticks - up_ticks)
        
        return round(target_ticks, 3)
    
    def get_next_state_position(self, picker_id):
        """
        Get next position based on picker state toggle (mimics GuitarBotParser logic).
        
        Args:
            picker_id: Picker motor ID
            
        Returns:
            Tuple of (target_position_ticks, new_state)
        """
        if picker_id not in self.motor_info:
            return None, None
        
        # Toggle state (like GuitarBotParser does)
        current_state = self.picker_states[picker_id]
        new_state = not current_state
        self.picker_states[picker_id] = new_state
        
        # Choose destination based on NEW state
        if new_state == 0:  # Going to down
            target_ticks = self.motor_info[picker_id]['down_ticks']
        else:  # Going to up
            target_ticks = self.motor_info[picker_id]['up_ticks']
        
        return target_ticks, new_state
    
    def generate_pluck_trajectory(self, picker_id, target_position, num_points=tu.PICKER_PLUCK_MOTION_POINTS):
        """
        Generate smooth plucking trajectory for a single picker motor.
        
        Args:
            picker_id: Picker motor ID
            target_position: Target position in encoder ticks
            num_points: Number of trajectory points
            
        Returns:
            Trajectory array or None if error
        """
        if picker_id not in self.current_positions:
            print(f"Error: Picker {picker_id} not configured")
            return None
        
        start_position = self.current_positions[picker_id]
        
        # Use GuitarBotParser's interp_with_blend for smooth motion
        trajectory = GuitarBotParser.interp_with_blend(
            start_position, 
            target_position, 
            num_points, 
            tu.TRAJECTORY_BLEND_PERCENT
        )
        
        # Handle case where interp_with_blend returns None
        if trajectory is None:
            trajectory = np.linspace(start_position, target_position, num_points)
        
        return trajectory
    
    def parse_pluck_message(self, midi_note, velocity=100, use_velocity_mapping=True):
        """
        Parse pluck message for single note with velocity control.
        
        Args:
            midi_note: MIDI note number
            velocity: MIDI velocity (0-127)
            use_velocity_mapping: If True, use velocity for position; if False, use state toggle
            
        Returns:
            List of 15-element position arrays for complete robot trajectory
        """
        print(f"Processing pluck: MIDI {midi_note}, Velocity {velocity}, "
              f"Velocity mapping: {use_velocity_mapping}")
        
        # Map MIDI note to picker
        picker_id = self.midi_note_to_picker_id(midi_note)
        if picker_id is None:
            print(f"Error: MIDI note {midi_note} not supported by available pickers")
            return []
        
        # Determine target position
        if use_velocity_mapping:
            target_pos = self.velocity_to_position(picker_id, velocity)
            if target_pos is None:
                print(f"Error: Could not calculate position for picker {picker_id}")
                return []
        else:
            # Use state-based toggle (like DynamicsParser)
            target_pos, new_state = self.get_next_state_position(picker_id)
            if target_pos is None:
                print(f"Error: Picker {picker_id} not configured")
                return []
        
        # Generate trajectory
        trajectory = self.generate_pluck_trajectory(picker_id, target_pos)
        if trajectory is None:
            return []
        
        # Update current position
        self.current_positions[picker_id] = target_pos
        
        # Create 15-element trajectory arrays
        trajectories_list = []
        for point in trajectory:
            # Start with initial_point as template
            full_position = tu.initial_point.copy()
            
            # Update picker position (pickers start at index 12)
            picker_motor_index = 12 + picker_id
            full_position[picker_motor_index] = int(point)
            
            trajectories_list.append(full_position)
        
        # Calculate velocity info for logging
        if use_velocity_mapping:
            velocity_ratio = velocity / 127.0
            up_mm = self.motor_info[picker_id]['up_mm']
            down_mm = self.motor_info[picker_id]['down_mm']
            target_mm = up_mm + velocity_ratio * (down_mm - up_mm)
            
            print(f"Generated pluck trajectory: MIDI {midi_note} -> Picker {picker_id}, "
                  f"Velocity {velocity} -> {target_mm:.2f}mm ({target_pos:.1f} ticks)")
        else:
            state_name = 'down' if self.picker_states[picker_id] == 0 else 'up'
            print(f"Generated pluck trajectory: MIDI {midi_note} -> Picker {picker_id}, "
                  f"State toggle -> {state_name} ({target_pos:.1f} ticks)")
        
        return trajectories_list
    
    def parse_dynamics_message(self, midi_notes, use_velocity_mapping=False):
        """
        Parse /Dyn message containing list of MIDI note numbers (state-based plucking).
        
        Args:
            midi_notes: List of MIDI note numbers to trigger
            use_velocity_mapping: If True, use default velocity; if False, use state toggle
            
        Returns:
            List of 15-element position arrays for complete robot trajectory
        """
        print(f"Processing /Dyn message: {midi_notes}")
        
        # Group notes by picker
        picker_actions = {}
        for midi_note in midi_notes:
            picker_id = self.midi_note_to_picker_id(midi_note)
            if picker_id is not None:
                if picker_id not in picker_actions:
                    picker_actions[picker_id] = []
                picker_actions[picker_id].append(midi_note)
            else:
                print(f"Warning: MIDI note {midi_note} not supported")
        
        # Generate trajectories for each active picker
        all_trajectories = {}
        max_length = 0
        
        for picker_id in self.motor_info:
            if picker_id in picker_actions:
                # Picker has actions - generate trajectory
                if use_velocity_mapping:
                    # Use default velocity for dynamics testing
                    target_pos = self.velocity_to_position(picker_id, 100)
                else:
                    # Use state toggle
                    target_pos, new_state = self.get_next_state_position(picker_id)
                
                trajectory = self.generate_pluck_trajectory(picker_id, target_pos)
                self.current_positions[picker_id] = target_pos
                
                state_name = 'down' if self.picker_states[picker_id] == 0 else 'up'
                print(f"Picker {picker_id}: {target_pos:.1f} ticks ({state_name})")
                
            else:
                # Picker stays at current position
                trajectory = np.full(tu.PICKER_PLUCK_MOTION_POINTS, 
                                   self.current_positions[picker_id])
            
            all_trajectories[picker_id] = trajectory
            if trajectory is not None:
                max_length = max(max_length, len(trajectory))
        
        # Create combined trajectory matrix
        trajectories_list = []
        for i in range(max_length):
            # Create full 15-motor position array
            full_position = tu.initial_point.copy()
            
            # Update picker positions
            for picker_id, traj in all_trajectories.items():
                picker_motor_index = 12 + picker_id
                if i < len(traj):
                    full_position[picker_motor_index] = int(traj[i])
                else:
                    full_position[picker_motor_index] = int(traj[-1])
            
            trajectories_list.append(full_position)
        
        print(f"Generated {len(trajectories_list)} trajectory points")
        
        # Plot if graphing enabled
        if tu.graph:
            self.plot_trajectories(trajectories_list)
        
        return trajectories_list
    
    def reset_positions(self):
        """Reset all picker motors to up position."""
        print("Resetting all picker motors to up position")
        self.picker_states = {picker_id: 1 for picker_id in self.motor_info}
        for picker_id in self.motor_info:
            self.current_positions[picker_id] = self.motor_info[picker_id]['up_ticks']
    
    def get_status(self):
        """Get current status of all picker motors."""
        status = {}
        for picker_id in self.motor_info:
            state = self.picker_states[picker_id]
            pos_ticks = self.current_positions[picker_id]
            
            # Convert back to mm for display
            resolution = self.motor_info[picker_id]['resolution']
            pos_mm = (pos_ticks * tu.MM_TO_ENCODER_CONVERSION_FACTOR) / resolution
            
            motor_id = 12 + picker_id  # Actual motor index in 15-motor array
            status[f'picker_{picker_id}'] = {
                'motor_id': motor_id,
                'position_ticks': pos_ticks,
                'position_mm': round(pos_mm, 2),
                'state': 'up' if state == 1 else 'down'
            }
        
        return status
    
    def plot_trajectories(self, trajectories_list, title="Right Hand Trajectories"):
        """Plot picker motor trajectories."""
        if not trajectories_list:
            print("No trajectories to plot")
            return
        
        fig = go.Figure()
        
        # Create time axis
        timestamps = [i * tu.TIME_STEP for i in range(len(trajectories_list))]
        
        # Add traces for picker motors (indices 12, 13, 14)
        for picker_id in self.motor_info:
            motor_index = 12 + picker_id
            y_values = [traj[motor_index] for traj in trajectories_list]
            
            fig.add_trace(
                go.Scatter(
                    x=timestamps, 
                    y=y_values, 
                    mode='lines+markers', 
                    name=f'Picker {picker_id} (Motor {motor_index})',
                    line=dict(width=3),
                    marker=dict(size=4)
                )
            )
        
        fig.update_layout(
            title=title,
            xaxis_title='Time (seconds)',
            yaxis_title='Motor Position (encoder ticks)',
            legend_title='Picker Motors',
            showlegend=True,
            hovermode='x unified',
            template='plotly_white'
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        fig.show()


# Example usage and testing
if __name__ == "__main__":
    parser = RightHandParser()
    
    print("=== Right Hand Parser Test ===")
    print("Available pickers:", list(parser.motor_info.keys()))
    
    print("\n=== Initial Status ===")
    status = parser.get_status()
    for picker_id, info in status.items():
        print(f"{picker_id}: Motor {info['motor_id']}, {info['position_ticks']:.1f} ticks "
              f"({info['position_mm']:.2f}mm) - {info['state']}")
    
    print("\n=== Test 1: Velocity-based plucking ===")
    # Test velocity-based plucking
    traj1 = parser.parse_pluck_message(midi_note=42, velocity=127, use_velocity_mapping=True)
    traj2 = parser.parse_pluck_message(midi_note=55, velocity=64, use_velocity_mapping=True)
    traj3 = parser.parse_pluck_message(midi_note=65, velocity=32, use_velocity_mapping=True)
    
    print("\n=== Test 2: State-based plucking ===")
    # Test state-based plucking (like original DynamicsParser)
    traj4 = parser.parse_pluck_message(midi_note=42, use_velocity_mapping=False)
    traj5 = parser.parse_pluck_message(midi_note=42, use_velocity_mapping=False)  # Should toggle
    
    print("\n=== Test 3: Dynamics message ===")
    # Test /Dyn message (multiple notes)
    traj6 = parser.parse_dynamics_message([41, 52, 63])
    
    print(f"\nSample trajectory shape: {len(traj6)} points × {len(traj6[0])} motors")
    print(f"Duration: {len(traj6) * tu.TIME_STEP:.3f} seconds")
    
    print("\n=== Final Status ===")
    status = parser.get_status()
    for picker_id, info in status.items():
        print(f"{picker_id}: Motor {info['motor_id']}, {info['position_ticks']:.1f} ticks "
              f"({info['position_mm']:.2f}mm) - {info['state']}")
    
    print("\n=== Test Complete ===")