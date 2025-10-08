"""
LeftHandParser.py - Left hand trajectory generation for fretting calibration

Handles /Fret OSC messages to test left hand fretting motor dynamics.
Focuses purely on fretting robotics - trajectory generation and motor control.

Motor Layout (Left Hand - First 12 motors of 15-motor array):
- Motors 0-5: Slider motors (one per string, move to fret positions)  
- Motors 6-11: Presser motors (one per string, press onto frets)

/Fret Message Format:
- midi_note_number: MIDI note (40-68, mapped to string/fret)
- presser_force: Force level (0.0-1.0, optional)

Note: Right-hand plucking functionality moved to RightHandParser.py
"""

import numpy as np
import copy
from GuitarBotParser import GuitarBotParser  # Import for reusing interp_with_blend
import tune as tu
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class LeftHandParser:
    def __init__(self):
        # Current state tracking for all 12 LH motors (use initial_point from tune.py)
        self.current_positions = tu.initial_point[:12].copy()  # First 12 motors only
        
        # String/fret state tracking 
        self.string_states = {i: {'fret': 0, 'pressed': False} for i in range(6)}
    
    def string_fret_to_slider_position(self, string_id, fret_num):
        """
        Convert string/fret combination to slider motor position.
        
        Args:
            string_id: String index (0-5)
            fret_num: Fret number (0 for open, 1+ for frets)
            
        Returns:
            Slider position in encoder ticks
        """
        if fret_num == 0:  # Open string
            return tu.SLIDER_ENCODER_OFFSET  # Base position
        
        if fret_num > len(tu.SLIDER_MM_PER_FRET):
            print(f"Warning: Fret {fret_num} exceeds calibrated range")
            fret_num = len(tu.SLIDER_MM_PER_FRET)
        
        # Get physical position from tune.py calibration
        fret_mm = tu.SLIDER_MM_PER_FRET[fret_num - 1]  # Array is 0-indexed, but fret 1 = index 0
        
        # Convert mm to encoder ticks (same formula as GuitarBotParser)
        # Account for motor direction multiplier
        direction = tu.SLIDER_MOTOR_DIRECTION[string_id]
        encoder_ticks = (fret_mm * direction * 1024) / tu.MM_TO_ENCODER_CONVERSION_FACTOR  # Assuming 1024 resolution
        
        # Add offset
        final_position = encoder_ticks + tu.SLIDER_ENCODER_OFFSET
        
        return round(final_position, 3)
    
    def get_presser_position(self, string_id, fret_num, presser_force=None):
        """
        Get presser position for string/fret combination.
        
        Args:
            string_id: String index (0-5)
            fret_num: Fret number (0 for open, 1+ for frets)
            presser_force: Optional force override (0.0-1.0, None uses default)
            
        Returns:
            Presser position in encoder ticks
        """
        if fret_num == 0:  # Open string - don't press
            return tu.LH_PRESSER_UNPRESSED_POS
        
        # Use force parameter if provided, otherwise use default
        if presser_force is not None:
            # Scale between unpressed and pressed positions
            force_range = tu.LH_PRESSER_PRESSED_POS - tu.LH_PRESSER_UNPRESSED_POS
            position = tu.LH_PRESSER_UNPRESSED_POS + (presser_force * force_range)
            return round(position, 3)
        else:
            # Use default pressed position
            return tu.LH_PRESSER_PRESSED_POS
    
    def generate_fret_trajectory(self, string_id, fret_num, presser_force=None, 
                                num_points=tu.PRESSER_INTERPOLATION_POINTS):
        """
        Generate trajectory for fretting a single string at a specific fret.
        Uses 3-phase motion: unpress → slide → press (mimics GuitarBotParser pattern)
        
        Args:
            string_id: String index (0-5)
            fret_num: Fret number (0=open, 1-24=frets)
            presser_force: Optional force level (0.0-1.0)
            num_points: Points per trajectory phase
            
        Returns:
            List of 15-element arrays representing full robot trajectory
        """
        print(f"Generating fret trajectory: String {string_id}, Fret {fret_num}, Force: {presser_force}")
        
        # Calculate target positions
        slider_motor_id = string_id
        presser_motor_id = string_id + 6
        
        target_slider_pos = self.string_fret_to_slider_position(string_id, fret_num)
        target_presser_pos = self.get_presser_position(string_id, fret_num, presser_force)
        
        # Get current positions
        current_slider_pos = self.current_positions[slider_motor_id]
        current_presser_pos = self.current_positions[presser_motor_id]
        
        # Generate 3-phase trajectory
        all_trajectory_points = []
        
        # Phase 1: UNPRESS - Release presser while holding slider
        phase1_slider = GuitarBotParser.interp_with_blend(
            current_slider_pos, current_slider_pos, num_points, tu.TRAJECTORY_BLEND_PERCENT
        )
        phase1_presser = GuitarBotParser.interp_with_blend(
            current_presser_pos, tu.LH_PRESSER_UNPRESSED_POS, num_points, tu.TRAJECTORY_BLEND_PERCENT
        )
        
        # Handle case where interp_with_blend returns None
        if phase1_slider is None:
            phase1_slider = np.full(num_points, current_slider_pos)
        if phase1_presser is None:
            phase1_presser = np.linspace(current_presser_pos, tu.LH_PRESSER_UNPRESSED_POS, num_points)
        
        # Phase 2: SLIDE - Move slider to target while keeping presser unpressed
        phase2_slider = GuitarBotParser.interp_with_blend(
            current_slider_pos, target_slider_pos, tu.LH_SINGLE_NOTE_MOTION_POINTS, tu.TRAJECTORY_BLEND_PERCENT
        )
        phase2_presser = GuitarBotParser.interp_with_blend(
            tu.LH_PRESSER_UNPRESSED_POS, tu.LH_PRESSER_UNPRESSED_POS, tu.LH_SINGLE_NOTE_MOTION_POINTS, tu.TRAJECTORY_BLEND_PERCENT
        )
        
        if phase2_slider is None:
            phase2_slider = np.linspace(current_slider_pos, target_slider_pos, tu.LH_SINGLE_NOTE_MOTION_POINTS)
        if phase2_presser is None:
            phase2_presser = np.full(tu.LH_SINGLE_NOTE_MOTION_POINTS, tu.LH_PRESSER_UNPRESSED_POS)
        
        # Phase 3: PRESS - Apply presser force while holding slider position
        phase3_slider = GuitarBotParser.interp_with_blend(
            target_slider_pos, target_slider_pos, num_points, tu.TRAJECTORY_BLEND_PERCENT
        )
        phase3_presser = GuitarBotParser.interp_with_blend(
            tu.LH_PRESSER_UNPRESSED_POS, target_presser_pos, num_points, tu.TRAJECTORY_BLEND_PERCENT
        )
        
        if phase3_slider is None:
            phase3_slider = np.full(num_points, target_slider_pos)
        if phase3_presser is None:
            phase3_presser = np.linspace(tu.LH_PRESSER_UNPRESSED_POS, target_presser_pos, num_points)
        
        # Combine all phases
        combined_slider = np.concatenate([phase1_slider, phase2_slider, phase3_slider])
        combined_presser = np.concatenate([phase1_presser, phase2_presser, phase3_presser])
        
        # Create 15-element trajectory arrays
        max_length = len(combined_slider)
        
        for i in range(max_length):
            # Start with initial_point as template
            full_position = tu.initial_point.copy()
            
            # Update the specific slider and presser motors
            full_position[slider_motor_id] = int(combined_slider[i])
            full_position[presser_motor_id] = int(combined_presser[i])
            
            all_trajectory_points.append(full_position)
        
        # Update current positions for this string
        self.current_positions[slider_motor_id] = target_slider_pos
        self.current_positions[presser_motor_id] = target_presser_pos
        self.string_states[string_id] = {'fret': fret_num, 'pressed': fret_num > 0}
        
        print(f"Generated {len(all_trajectory_points)} trajectory points")
        print(f"Final positions - Slider: {target_slider_pos}, Presser: {target_presser_pos}")
        
        return all_trajectory_points
    
    def parse_fret_message(self, midi_note_number, presser_force=None):
        """
        Parse a /Fret OSC message and generate fretting trajectory.
        
        Args:
            midi_note_number: MIDI note number (40-68 based on STRING_MIDI_RANGES)
            presser_force: Optional force level (0.0-1.0)
            
        Returns:
            List of 15-element position arrays for fretting trajectory
        """
        print(f"Processing /Fret message: MIDI Note {midi_note_number}, Force {presser_force}")
        
        # Validate MIDI note number and map to string/fret
        string_fret_info = self.midi_note_to_string_fret(midi_note_number)
        if not string_fret_info:
            print(f"Error: MIDI note {midi_note_number} not playable on available strings.")
            return []
        
        string_id, fret_num = string_fret_info
        
        # Validate inputs
        if presser_force is not None and not (0.0 <= presser_force <= 1.0):
            print(f"Error: Invalid presser_force {presser_force}. Must be 0.0-1.0.")
            return []
        
        # Generate fretting trajectory
        trajectory = self.generate_fret_trajectory(string_id, fret_num, presser_force)
        
        # Plot if graphing is enabled
        if tu.graph:
            print(f"Plotting trajectory for MIDI note {midi_note_number}")
            self.plot_trajectories(trajectory)
        
        return trajectory
    
    def midi_note_to_string_fret(self, midi_note):
        """
        Convert MIDI note number to string ID and fret number.
        
        Args:
            midi_note: MIDI note number
            
        Returns:
            Tuple (string_id, fret_num) or None if not playable
        """
        # Check each string's MIDI range
        for string_id, (low_note, high_note, direction) in enumerate(tu.STRING_MIDI_RANGES):
            if low_note <= midi_note <= high_note:
                # Calculate fret number: fret = midi_note - open_string_note
                fret_num = midi_note - low_note
                if 0 <= fret_num <= 24:  # Valid fret range
                    return (string_id, fret_num)
        
        return None  # Note not playable on any string
    

    
    def reset_positions(self):
        """Reset all LH motors to initial positions."""
        print("Resetting all LH motors to initial positions")
        self.current_positions = tu.initial_point[:12].copy()
        self.string_states = {i: {'fret': 0, 'pressed': False} for i in range(6)}
    
    def get_status(self):
        """Get current status of all LH motors and string states."""
        status = {
            'motor_positions': self.current_positions.copy(),
            'string_states': self.string_states.copy()
        }
        
        # Add human-readable info
        for string_id in range(6):
            slider_pos = self.current_positions[string_id]
            presser_pos = self.current_positions[string_id + 6]
            fret_num = self.string_states[string_id]['fret']
            
            status[f'string_{string_id}'] = {
                'fret': fret_num,
                'slider_position': slider_pos,
                'presser_position': presser_pos,
                'pressed': self.string_states[string_id]['pressed']
            }
        
        return status
    
    def plot_trajectories(self, trajectories_list, title="Left Hand Trajectories"):
        """Plot LH motor trajectories with enhanced visualization."""
        if not trajectories_list or len(trajectories_list) < 12:
            print("Insufficient trajectory data for plotting")
            return
        
        # Create time axis
        num_points = len(trajectories_list[0])
        timestamps = [i * tu.TIME_STEP for i in range(num_points)]
        
        # Create subplots for sliders and pressers
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Slider Motors (0-5)', 'Presser Motors (6-11)'),
            vertical_spacing=0.1
        )
        
        # Plot slider motors (0-5)
        for motor_idx in range(6):
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=trajectories_list[motor_idx],
                    mode='lines+markers',
                    name=f'Slider {motor_idx}',
                    line=dict(width=2),
                    marker=dict(size=3)
                ),
                row=1, col=1
            )
        
        # Plot presser motors (6-11)
        for motor_idx in range(6, 12):
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=trajectories_list[motor_idx],
                    mode='lines+markers',
                    name=f'Presser {motor_idx-6}',
                    line=dict(width=2),
                    marker=dict(size=3)
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            title=title,
            xaxis_title='Time (seconds)',
            yaxis_title='Motor Position (encoder ticks)',
            showlegend=True,
            height=800
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        fig.show()
    
# Example usage and testing  
if __name__ == "__main__":
    # Initialize parser
    parser = LeftHandParser()
    
    print("=== Left Hand Parser Test ===")
    
    # Test /Fret message processing with MIDI note numbers (fretting only)
    print("Testing /Fret message processing...")
    
    # Test MIDI note 40 (Low E open string)
    trajectory_open = parser.parse_fret_message(midi_note_number=40)
    print(f"MIDI 40 (Low E open): {len(trajectory_open)} trajectory points")
    
    # Test MIDI note 45 (5th fret on Low E) with specific force
    trajectory_fret5 = parser.parse_fret_message(midi_note_number=45, presser_force=0.8)
    print(f"MIDI 45 (Low E 5th fret): {len(trajectory_fret5)} trajectory points")
    
    # Test MIDI note 52 (D string open)
    trajectory_d_string = parser.parse_fret_message(midi_note_number=52, presser_force=0.6)
    print(f"MIDI 52 (D string): {len(trajectory_d_string)} trajectory points")
    
    # Test MIDI note 62 (B string)
    trajectory_b_string = parser.parse_fret_message(midi_note_number=62)
    print(f"MIDI 62 (B string): {len(trajectory_b_string)} trajectory points")
    
    # Check status
    print("\nCurrent status:")
    status = parser.get_status()
    for string_id in range(6):
        string_info = status[f'string_{string_id}']
        print(f"String {string_id}: Fret {string_info['fret']}, Pressed: {string_info['pressed']}")
    
    # Reset all positions  
    parser.reset_positions()
    print("\nPositions reset to initial state.")
    
    print("=== Test Complete ===")