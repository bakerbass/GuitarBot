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


class DynamicsParser:
    def __init__(self):
        # Track current state of each picker motor (0=down, 1=up)
        self.picker_states = {13: 1, 14: 1, 15: 1}  # Start in up position
        
        # Motor position mappings from tune.py
        self.motor_positions = {
            13: {'down': tu.PICKER_MOTOR_INFO[0]['down_pluck_mm'], 
                 'up': tu.PICKER_MOTOR_INFO[0]['up_pluck_mm']},
            14: {'down': tu.PICKER_MOTOR_INFO[1]['down_pluck_mm'],
                 'up': tu.PICKER_MOTOR_INFO[1]['up_pluck_mm']}, 
            15: {'down': tu.PICKER_MOTOR_INFO[2]['down_pluck_mm'],
                 'up': tu.PICKER_MOTOR_INFO[2]['up_pluck_mm']}
        }
        
        # Current positions (start at up positions)
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
        """Get the next position for a motor (toggle between up/down)."""
        current_state = self.picker_states[motor_id]
        if current_state == 1:  # Currently up, go down
            return self.motor_positions[motor_id]['down'], 0
        else:  # Currently down, go up
            return self.motor_positions[motor_id]['up'], 1
    
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
                # Get next position and update state
                target_pos, new_state = self.get_next_position(motor_id)
                self.picker_states[motor_id] = new_state
                
                # Generate trajectory
                trajectory = self.generate_trajectory(motor_id, target_pos)
                
                # Update current position
                self.current_positions[motor_index] = target_pos
                
                print(f"Motor {motor_id}: {self.current_positions[motor_index]:.1f}mm "
                      f"({'down' if new_state == 0 else 'up'})")
                
            else:  # Motor stays at current position
                trajectory = np.full(tu.PICKER_PLUCK_MOTION_POINTS, 
                                   self.current_positions[motor_index])
            
            all_trajectories.append(trajectory)
            max_length = max(max_length, len(trajectory))
        
        # Pad trajectories to same length and create combined trajectory matrix
        trajectories_list = []
        for i in range(max_length):
            # Create full 15-motor position array (12 LH + 3 RH)
            full_position = [0] * 12  # LH motors stay at 0 for dynamics testing
            
            # Add picker positions (motors 13, 14, 15)
            for motor_idx, traj in enumerate(all_trajectories):
                if i < len(traj):
                    full_position.append(int(traj[i]))
                else:
                    full_position.append(int(traj[-1]))  # Hold last position
            
            trajectories_list.append(full_position)
        
        print(f"Generated {len(trajectories_list)} trajectory points")
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
            pos = self.current_positions[motor_idx]
            status[motor_id] = {
                'position_mm': pos,
                'state': 'up' if state == 1 else 'down'
            }
        return status


# Example usage and testing
if __name__ == "__main__":
    parser = DynamicsParser()
    
    print("=== Initial Status ===")
    print(parser.get_status())
    
    print("\n=== Test 1: Single notes ===")
    # Test single note on each motor
    traj1 = parser.parse_dyn_message([42])  # Motor 13
    traj2 = parser.parse_dyn_message([55])  # Motor 14  
    traj3 = parser.parse_dyn_message([65])  # Motor 15
    
    print("\n=== Test 2: Multiple notes ===")
    # Test multiple notes (should toggle states)
    traj4 = parser.parse_dyn_message([41, 52, 63])  # All motors
    
    print("\n=== Final Status ===")
    print(parser.get_status())