"""
DynamicsParser.py - Simplified dynamics testing for plucking motors

Handles /Dyn OSC messages to test plucking motor dynamics without complex timing.
Routes MIDI note numbers to specific motors and toggles between up/down positions.

Motor Mapping:
- MNN 40-49 -> Motor 13 (Low E string area)  
- MNN 50-59 -> Motor 14 (D string area)
- MNN 60+   -> Motor 15 (B string area)
"""

import numpy as np
import copy
from GuitarBotParser import GuitarBotParser  # Import for reusing interp_with_blend
import tune as tu
import plotly.graph_objects as go


class DynamicsParser:
    def __init__(self):
        # Track current state of each picker motor (0=down, 1=up)
        self.picker_states = {13: 1, 14: 1, 15: 1}  # Start in up position
        
        # Motor position mappings from tune.py - convert mm to encoder ticks like GuitarBotParser
        self.motor_positions = {}
        for motor_id in [13, 14, 15]:
            picker_index = motor_id - 13  # Convert to 0-2 index for PICKER_MOTOR_INFO
            down_mm = tu.PICKER_MOTOR_INFO[picker_index]['down_pluck_mm']
            up_mm = tu.PICKER_MOTOR_INFO[picker_index]['up_pluck_mm']
            resolution = tu.PICKER_MOTOR_INFO[picker_index]['resolution']
            
            # Convert mm to encoder ticks using same formula as GuitarBotParser
            down_ticks = (down_mm * resolution) / tu.MM_TO_ENCODER_CONVERSION_FACTOR
            up_ticks = (up_mm * resolution) / tu.MM_TO_ENCODER_CONVERSION_FACTOR
            
            self.motor_positions[motor_id] = {
                'down': round(down_ticks, 3),
                'up': round(up_ticks, 3)
            }
        
        # Current positions in encoder ticks (start at up positions)
        self.current_positions = [
            self.motor_positions[13]['up'],  # Motor 13
            self.motor_positions[14]['up'],  # Motor 14  
            self.motor_positions[15]['up']   # Motor 15
        ]
    
    def mnn_to_motor_id(self, mnn):
        """Convert MIDI note number to motor ID."""
        if 40 <= mnn <= 49:
            return 13
        elif 50 <= mnn <= 59:
            return 14
        elif mnn >= 60:
            return 15
        else:
            raise ValueError(f"MNN {mnn} out of supported range (40+)")
    
    def get_next_position(self, motor_id):
        """Get the next position for a motor (toggle between up/down). 
        Mimics GuitarBotParser picker state logic."""
        current_state = self.picker_states[motor_id]
        picker_index = motor_id - 13
        
        # Toggle state first (like GuitarBotParser does)
        new_state = not current_state
        self.picker_states[motor_id] = new_state
        
        # Choose destination based on NEW state
        destination_key = 'down_pluck_mm' if new_state == 0 else 'up_pluck_mm'
        qf_mm = tu.PICKER_MOTOR_INFO[picker_index][destination_key]
        resolution = tu.PICKER_MOTOR_INFO[picker_index]['resolution']
        
        # Convert to encoder ticks (same formula as GuitarBotParser)
        pos_ticks = (qf_mm * resolution) / tu.MM_TO_ENCODER_CONVERSION_FACTOR
        
        return round(pos_ticks, 3), new_state
    
    def generate_trajectory(self, motor_id, target_position, num_points=tu.PICKER_PLUCK_MOTION_POINTS):
        """Generate smooth trajectory for a single motor using interp_with_blend."""
        motor_index = motor_id - 13  # Convert to array index (0, 1, 2)
        start_position = self.current_positions[motor_index]
        
        # Use the existing interp_with_blend function for smooth motion
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
    
    def parse_dyn_message(self, mnn_list):
        """
        Parse /Dyn message containing list of MIDI note numbers.
        
        Args:
            mnn_list: List of MIDI note numbers to trigger
            
        Returns:
            trajectories_list: List of position arrays for all 3 motors over time
        """
        print(f"Processing /Dyn message: {mnn_list}")
        
        # Group MNNs by motor
        motor_actions = {13: [], 14: [], 15: []}
        for mnn in mnn_list:
            try:
                motor_id = self.mnn_to_motor_id(mnn)
                motor_actions[motor_id].append(mnn)
            except ValueError as e:
                print(f"Warning: {e}")
        
        # Generate trajectories for each motor that has actions
        all_trajectories = []
        max_length = 0
        
        for motor_id in [13, 14, 15]:
            motor_index = motor_id - 13
            
            if motor_actions[motor_id]:  # Motor has actions
                # Get next position (state is updated inside get_next_position)
                target_pos, new_state = self.get_next_position(motor_id)
                
                # Generate trajectory
                trajectory = self.generate_trajectory(motor_id, target_pos)
                
                # Update current position
                self.current_positions[motor_index] = target_pos
                
                print(f"Motor {motor_id}: {self.current_positions[motor_index]:.1f} ticks "
                      f"({'down' if new_state == 0 else 'up'})")
                
            else:  # Motor stays at current position
                trajectory = np.full(tu.PICKER_PLUCK_MOTION_POINTS, 
                                   self.current_positions[motor_index])
            
            all_trajectories.append(trajectory)
            if trajectory is not None:
                max_length = max(max_length, len(trajectory))
            else:
                max_length = max(max_length, tu.PICKER_PLUCK_MOTION_POINTS)
        
        # Pad trajectories to same length and create combined trajectory matrix
        # Use initial_point format from tune.py to match GuitarBotParser output
        trajectories_list = []
        for i in range(max_length):
            # Create full 15-motor position array using initial_point as template
            full_position = tu.initial_point.copy()
            
            # Update picker positions (motors 13, 14, 15 are at indices 12, 13, 14)
            for motor_idx, traj in enumerate(all_trajectories):
                array_index = 12 + motor_idx  # Picker motors start at index 12
                if i < len(traj):
                    full_position[array_index] = int(traj[i])
                else:
                    full_position[array_index] = int(traj[-1])  # Hold last position
            
            trajectories_list.append(full_position)
        
        print(f"Generated {len(trajectories_list)} trajectory points")
        
        # Plot trajectories if graphing is enabled (mimic GuitarBotParser behavior)
        if tu.graph:
            self.plot_trajectories(trajectories_list)
        
        return trajectories_list
    
    def reset_positions(self):
        """Reset all motors to up position."""
        print("Resetting all picker motors to up position")
        self.picker_states = {13: 1, 14: 1, 15: 1}
        self.current_positions = [
            self.motor_positions[13]['up'],
            self.motor_positions[14]['up'], 
            self.motor_positions[15]['up']
        ]
    
    def get_status(self):
        """Get current status of all picker motors."""
        status = {}
        for motor_id in [13, 14, 15]:
            motor_idx = motor_id - 13
            state = self.picker_states[motor_id]
            pos_ticks = self.current_positions[motor_idx]
            
            # Convert back to mm for display (reverse of the conversion)
            picker_index = motor_id - 13
            resolution = tu.PICKER_MOTOR_INFO[picker_index]['resolution']
            pos_mm = (pos_ticks * tu.MM_TO_ENCODER_CONVERSION_FACTOR) / resolution
            
            status[motor_id] = {
                'position_ticks': pos_ticks,
                'position_mm': round(pos_mm, 2),
                'state': 'up' if state == 1 else 'down'
            }
        return status
    
    def plot_trajectories(self, trajectories_list):
        """
        Plot motor trajectories using plotly, mimicking GuitarBotParser's plotting routine.
        """
        if not trajectories_list:
            print("No trajectories to plot")
            return
        
        fig = go.Figure()
        
        # Create time axis
        timestamps = [i * tu.TIME_STEP for i in range(len(trajectories_list))]
        
        # Add traces for picker motors only (motors 12, 13, 14 in the array = motors 13, 14, 15)
        picker_motor_indices = [12, 13, 14]  # Array indices for motors 13, 14, 15
        picker_motor_names = [13, 14, 15]    # Actual motor IDs
        
        for i, (motor_idx, motor_id) in enumerate(zip(picker_motor_indices, picker_motor_names)):
            y_values = [traj[motor_idx] for traj in trajectories_list]
            
            # Add trace with motor-specific styling
            fig.add_trace(
                go.Scatter(
                    x=timestamps, 
                    y=y_values, 
                    mode='lines+markers', 
                    name=f'Motor {motor_id} (Picker {i+1})',
                    line=dict(width=3),
                    marker=dict(size=4)
                )
            )
        
        # Update layout to match GuitarBotParser style
        fig.update_layout(
            title='Dynamics Test - Picker Motor Trajectories',
            xaxis_title='Time (seconds)',
            yaxis_title='Motor Position (encoder ticks)',
            legend_title='Picker Motors',
            showlegend=True,
            hovermode='x unified',
            template='plotly_white'
        )
        
        # Add grid for better readability
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
        
        # Show the plot
        print("Displaying dynamics trajectory plot...")
        fig.show()


# Example usage and testing
if __name__ == "__main__":
    parser = DynamicsParser()
    
    print("=== Initial Status (Encoder Ticks) ===")
    status = parser.get_status()
    for motor_id, info in status.items():
        print(f"Motor {motor_id}: {info['position_ticks']:.1f} ticks ({info['position_mm']:.2f}mm) - {info['state']}")
    
    print(f"\n=== Tune.py Values ===")
    print(f"TIME_STEP: {tu.TIME_STEP}")
    print(f"PICKER_PLUCK_MOTION_POINTS: {tu.PICKER_PLUCK_MOTION_POINTS}")
    print(f"MM_TO_ENCODER_CONVERSION_FACTOR: {tu.MM_TO_ENCODER_CONVERSION_FACTOR}")
    
    print("\n=== Test 1: Single notes ===")
    # Test single note on each motor
    traj1 = parser.parse_dyn_message([42])  # Motor 13
    traj2 = parser.parse_dyn_message([55])  # Motor 14  
    traj3 = parser.parse_dyn_message([65])  # Motor 15
    
    print(f"\nTrajectory length: {len(traj1)} points, duration: {len(traj1) * tu.TIME_STEP:.3f}s")
    print(f"Sample trajectory point (all 15 motors): {traj1[0]}")
    print(f"Final picker positions: [{traj1[-1][12]}, {traj1[-1][13]}, {traj1[-1][14]}]")
    
    print("\n=== Test 2: Multiple notes ===")
    # Test multiple notes (should toggle states)
    traj4 = parser.parse_dyn_message([41, 52, 63])  # All motors
    
    print("\n=== Final Status (Encoder Ticks) ===")
    status = parser.get_status()
    for motor_id, info in status.items():
        print(f"Motor {motor_id}: {info['position_ticks']:.1f} ticks ({info['position_mm']:.2f}mm) - {info['state']}")