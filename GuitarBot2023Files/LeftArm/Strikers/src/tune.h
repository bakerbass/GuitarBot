#ifndef TUNE_H
#define TUNE_H

// strikerController.h
const float start_state_PICK[3] = {8, 4, 6}; // Picker encoder start position
const int   motor_id_PICK[3] = {13, 14, 15}; // maybe this goes in def...

// epos4.cpp
// homing offsets
const int   home_offset_SLIDE = 50000; //52000
const int   home_offset_PRESS = -25;
const int   home_offset_PICK  = 0;

const int   current_control_SLIDE[2] = {1575853, 4837093}; // p, i
const int   current_control_PICK[2] = {1042729, 2976309}; // p, i
const int   current_control_PRESS[2] = {3456649, 10257}; // p, i

const int   pos_control_SLIDE[5] = {6933308, 139254287, 104848, 10219, 637}; // p, i, d, v, a
const int   pos_control_PICK[5] = {18462573, 157853228, 170004, 9945, 585}; // p, i, d, v, a
const int   pos_control_PRESS[5] = {200000, 905480, 2643, 507, 36}; // p, i, d, v, a


#endif // TUNE_H