//
// Created by Raghavasimhan Sankaranarayanan on 03/30/22.
//

#ifndef SHIMON_DEF_H
#define SHIMON_DEF_H
#define NUM_STRIKERS 6
#define NUM_PRESSERS 6
#define TOTAL_CONTROLLERS 6
#define NUT_POS 0

#define ENCODER_DIR 1


const int kStrikerDirection[13] = { 0, 0, 1, 0, 0, 1, 1, 1, 0,0,0,0,0 }; // 0 is normal, 1 is flipped, idx 0 is dummy

#define HOME_POSITION 25 // Deg
#define P2P_MULT 100.f
#define MAX_TRAJ_POINTS 70
#define SCALE_LENGTH 648
#define NUM_POINTS_IN_TRAJ_FOR_HIT 70  // Make sure Hit > up
#define NUM_POINTS_IN_TRAJ_FOR_UP 0

#define CLEAR_FAULT_TIMER_INTERVAL 100   // ms



#define MAX_STRIKER_ANGLE_DEG 180
#endif // SHIMON_DEF_H
