"""
Parser.py - Orchestrates left and right hand parsers for complete note production

Combines LeftHandParser and RightHandParser to generate coordinated trajectories.
Similar in scope to GuitarBotParser but focused on dataset generation approach
for optimizing fretting force (/Fret messages) and dynamic range (/Dyn messages).

Key Features:
- Coordinates fretting and plucking for complete note production
- Handles both /Fret (fret + pluck) and /Dyn (pluck only) messages  
- Generates combined 15-motor trajectories
- Supports dataset generation workflows
- Maintains timing synchronization between hands
"""

import numpy as np
import copy
from LeftHandParser import LeftHandParser
from RightHandParser import RightHandParser
from GuitarBotParser import GuitarBotParser  # For interp_with_blend
import tune as tu
import plotly.graph_objects as go


class Parser:
    def __init__(self):
        # Initialize both hand parsers
        self.left_hand = LeftHandParser()
        self.right_hand = RightHandParser()
        
        # Timing coordination
        self.prep_time_before_pluck = tu.LH_PREP_TIME_BEFORE_PICK  # LH moves before RH plucks
        
    def parse_note_message(self, midi_note, presser_force=None, pluck_velocity=100, 
                          use_velocity_mapping=True):
        """
        Parse complete note message - coordinates fretting and plucking.
        
        Args:
            midi_note: MIDI note number
            presser_force: Fretting force (0.0-1.0, optional)
            pluck_velocity: Plucking velocity (0-127)
            use_velocity_mapping: If True, use velocity for pluck depth; if False, use state toggle
            
        Returns:
            Combined trajectory with coordinated left and right hand motion
        """
        print(f"\\n=== Processing Note: MIDI {midi_note} ===")
        print(f"Presser force: {presser_force}, Pluck velocity: {pluck_velocity}")
        
        # Generate left hand trajectory (fretting)
        print("Generating fretting trajectory...")
        lh_trajectory = self.left_hand.parse_fret_message(midi_note, presser_force)
        
        if not lh_trajectory:
            print("Error: Could not generate fretting trajectory")
            return []
        
        # Generate right hand trajectory (plucking)
        print("Generating plucking trajectory...")
        rh_trajectory = self.right_hand.parse_pluck_message(
            midi_note, pluck_velocity, use_velocity_mapping
        )
        
        if not rh_trajectory:
            print("Error: Could not generate plucking trajectory")
            return []
        
        # Coordinate timing - LH moves first, then RH plucks
        coordinated_trajectory = self.coordinate_trajectories(lh_trajectory, rh_trajectory)
        
        print(f"Generated coordinated trajectory: {len(coordinated_trajectory)} points, "
              f"Duration: {len(coordinated_trajectory) * tu.TIME_STEP:.3f}s")
        
        # Plot if graphing enabled
        if tu.graph:
            self.plot_combined_trajectory(coordinated_trajectory, f"Note MIDI {midi_note}")
        
        return coordinated_trajectory
    
    def parse_fret_only_message(self, midi_note, presser_force=None):
        """
        Parse /Fret message for fretting only (no plucking).
        
        Args:
            midi_note: MIDI note number
            presser_force: Fretting force (0.0-1.0)
            
        Returns:
            Fretting trajectory (15-motor format)
        """
        print(f"\\n=== Processing Fret-Only: MIDI {midi_note} ===")
        
        trajectory = self.left_hand.parse_fret_message(midi_note, presser_force)
        
        if tu.graph and trajectory:
            self.plot_combined_trajectory(trajectory, f"Fret-Only MIDI {midi_note}")
        
        return trajectory
    
    def parse_dynamics_message(self, midi_notes, use_velocity_mapping=False):
        """
        Parse /Dyn message for plucking only (no fretting changes).
        
        Args:
            midi_notes: List of MIDI note numbers
            use_velocity_mapping: If True, use velocity control; if False, use state toggle
            
        Returns:
            Plucking trajectory (15-motor format)
        """
        print(f"\\n=== Processing Dynamics: {midi_notes} ===")
        
        trajectory = self.right_hand.parse_dynamics_message(midi_notes, use_velocity_mapping)
        
        if tu.graph and trajectory:
            self.plot_combined_trajectory(trajectory, f"Dynamics {midi_notes}")
        
        return trajectory
    
    def coordinate_trajectories(self, lh_trajectory, rh_trajectory):
        """
        Coordinate left and right hand trajectories with proper timing.
        
        Args:
            lh_trajectory: Left hand trajectory
            rh_trajectory: Right hand trajectory
            
        Returns:
            Combined trajectory with coordinated timing
        """
        if not lh_trajectory or not rh_trajectory:
            return lh_trajectory or rh_trajectory or []
        
        # Calculate prep time in trajectory points
        prep_points = max(1, int(self.prep_time_before_pluck / tu.TIME_STEP))
        
        print(f"Coordinating trajectories: LH {len(lh_trajectory)} points, "
              f"RH {len(rh_trajectory)} points, Prep time: {prep_points} points")
        
        # Method 1: Sequential execution (LH first, then RH with overlap)
        if len(lh_trajectory) >= prep_points:
            # LH trajectory is long enough - start RH during LH motion
            combined_trajectory = []
            
            # Phase 1: LH motion only (prep phase)
            for i in range(prep_points):
                combined_trajectory.append(lh_trajectory[i].copy())
            
            # Phase 2: LH + RH coordinated motion
            lh_remaining = lh_trajectory[prep_points:]
            max_remaining = max(len(lh_remaining), len(rh_trajectory))
            
            for i in range(max_remaining):
                # Start with base position
                if i < len(lh_remaining):
                    combined_point = lh_remaining[i].copy()
                else:
                    combined_point = lh_trajectory[-1].copy()  # Hold LH final position
                
                # Add RH motion
                if i < len(rh_trajectory):
                    # Copy RH motor positions (indices 12-14)
                    for motor_idx in [12, 13, 14]:
                        combined_point[motor_idx] = rh_trajectory[i][motor_idx]
                
                combined_trajectory.append(combined_point)
            
        else:
            # LH trajectory is short - use simple concatenation
            combined_trajectory = lh_trajectory.copy()
            
            # Extend with RH motion
            for rh_point in rh_trajectory:
                # Use last LH position as base
                combined_point = combined_trajectory[-1].copy()
                
                # Add RH motion
                for motor_idx in [12, 13, 14]:
                    combined_point[motor_idx] = rh_point[motor_idx]
                
                combined_trajectory.append(combined_point)
        
        return combined_trajectory
    
    def parse_chord_sequence(self, chord_events, pluck_events=None):
        """
        Parse sequence of chord events with optional plucking.
        
        Args:
            chord_events: List of (midi_notes_list, timestamp, presser_force) tuples
            pluck_events: List of (midi_note, timestamp, velocity) tuples (optional)
            
        Returns:
            Combined trajectory for entire sequence
        """
        print(f"\\n=== Processing Chord Sequence: {len(chord_events)} chords ===")
        
        all_trajectories = []
        current_time = 0
        
        # Process each chord
        for i, (midi_notes, timestamp, presser_force) in enumerate(chord_events):
            print(f"\\nChord {i+1}: Notes {midi_notes} at t={timestamp}")
            
            # Generate fretting for multiple notes (chord)
            chord_trajectory = []
            for midi_note in midi_notes:
                note_traj = self.left_hand.parse_fret_message(midi_note, presser_force)
                if note_traj:
                    chord_trajectory.extend(note_traj)
            
            if chord_trajectory:
                all_trajectories.append((chord_trajectory, timestamp))
        
        # Add plucking events if provided
        if pluck_events:
            for midi_note, timestamp, velocity in pluck_events:
                pluck_traj = self.right_hand.parse_pluck_message(midi_note, velocity)
                if pluck_traj:
                    all_trajectories.append((pluck_traj, timestamp))
        
        # Sort by timestamp and combine
        all_trajectories.sort(key=lambda x: x[1])
        
        # Simple concatenation for now (could be enhanced with timing interpolation)
        combined_trajectory = []
        for trajectory, timestamp in all_trajectories:
            combined_trajectory.extend(trajectory)
        
        print(f"Generated chord sequence: {len(combined_trajectory)} total points")
        
        if tu.graph and combined_trajectory:
            self.plot_combined_trajectory(combined_trajectory, "Chord Sequence")
        
        return combined_trajectory
    
    def reset_all_positions(self):
        """Reset both left and right hand parsers to initial positions."""
        print("Resetting all motor positions")
        self.left_hand.reset_positions()
        self.right_hand.reset_positions()
    
    def get_combined_status(self):
        """Get status of both left and right hand parsers."""
        lh_status = self.left_hand.get_status()
        rh_status = self.right_hand.get_status()
        
        return {
            'left_hand': lh_status,
            'right_hand': rh_status,
            'timing': {
                'prep_time_seconds': self.prep_time_before_pluck,
                'prep_time_points': int(self.prep_time_before_pluck / tu.TIME_STEP)
            }
        }
    
    def plot_combined_trajectory(self, trajectory, title="Combined Trajectory"):
        """Plot complete 15-motor trajectory with left/right hand separation."""
        if not trajectory:
            print("No trajectory to plot")
            return
        
        fig = go.Figure()
        
        # Create time axis
        timestamps = [i * tu.TIME_STEP for i in range(len(trajectory))]
        
        # Plot left hand motors (0-11)
        for motor_idx in range(12):
            y_values = [point[motor_idx] for point in trajectory]
            motor_type = "Slider" if motor_idx < 6 else "Presser"
            string_id = motor_idx if motor_idx < 6 else motor_idx - 6
            
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=y_values,
                    mode='lines+markers',
                    name=f'LH {motor_type} {string_id}',
                    line=dict(width=2),
                    marker=dict(size=3),
                    legendgroup='left_hand'
                )
            )
        
        # Plot right hand motors (12-14)
        for motor_idx in range(12, 15):
            if motor_idx < len(trajectory[0]):  # Check if motor exists
                y_values = [point[motor_idx] for point in trajectory]
                picker_id = motor_idx - 12
                
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=y_values,
                        mode='lines+markers',
                        name=f'RH Picker {picker_id}',
                        line=dict(width=3),
                        marker=dict(size=4),
                        legendgroup='right_hand'
                    )
                )
        
        fig.update_layout(
            title=title,
            xaxis_title='Time (seconds)',
            yaxis_title='Motor Position (encoder ticks)',
            legend_title='Motors',
            showlegend=True,
            hovermode='x unified',
            template='plotly_white'
        )
        
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        fig.show()


# Example usage and testing
if __name__ == "__main__":
    parser = Parser()
    
    print("=== Parser Test - Coordinated Left/Right Hand ===")
    
    print("\\n=== Test 1: Complete Note Production ===")
    # Test complete note (fret + pluck)
    note_traj = parser.parse_note_message(
        midi_note=45,  # Low E 5th fret
        presser_force=0.8,
        pluck_velocity=100,
        use_velocity_mapping=True
    )
    
    print("\\n=== Test 2: Fret-Only Message ===") 
    # Test fretting without plucking
    fret_traj = parser.parse_fret_only_message(midi_note=52, presser_force=0.6)
    
    print("\\n=== Test 3: Dynamics-Only Message ===")
    # Test plucking without fretting
    dyn_traj = parser.parse_dynamics_message([42, 55, 65])
    
    print("\\n=== Test 4: Chord Sequence ===")
    # Test chord progression
    chord_events = [
        ([40, 52, 64], 0.0, 0.7),    # C major chord at t=0
        ([42, 54, 66], 2.0, 0.8),    # D major chord at t=2
    ]
    pluck_events = [
        (40, 0.5, 120),  # Pluck low E
        (52, 1.0, 100),  # Pluck D
    ]
    
    chord_traj = parser.parse_chord_sequence(chord_events, pluck_events)
    
    print("\\n=== Combined Status ===")
    status = parser.get_combined_status()
    
    print("Left Hand Status:")
    for string_id in range(6):
        if f'string_{string_id}' in status['left_hand']:
            info = status['left_hand'][f'string_{string_id}']
            print(f"  String {string_id}: Fret {info['fret']}, Pressed: {info['pressed']}")
    
    print("\\nRight Hand Status:")
    for picker_id, info in status['right_hand'].items():
        print(f"  {picker_id}: Motor {info['motor_id']}, {info['state']}, "
              f"{info['position_mm']:.2f}mm")
    
    print(f"\\nTiming: {status['timing']['prep_time_seconds']}s prep time "
          f"({status['timing']['prep_time_points']} points)")
    
    # Reset everything
    parser.reset_all_positions()
    
    print("\\n=== Test Complete ===")