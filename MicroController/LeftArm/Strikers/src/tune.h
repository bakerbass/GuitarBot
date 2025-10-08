#ifndef TUNE_H
#define TUNE_H

// strikerController.h

// Pick start position
/*
 * Higher number = higher position for plucker
 * Lower number = lower position for plucker
 * (as of 3 string prototype: Low E, D, B respectively
*/
// 8, 4, 6 before 9/3/2025
const float start_state_PICK[3] = {7.3f, 5.2f, 6.6f};

const int   motor_id_PICK[3] = {13, 14, 15}; // maybe this goes in def...

// epos4.cpp
// homing offsets
const int   home_offset_SLIDE = 50000; //52000
const int   home_offset_PRESS = -25;
const int   home_offset_PICK  = 0;

const uint32_t   current_control_SLIDE[2] = {1575853, 4837093}; // p, i
const uint32_t   current_control_PICK[2] = {1042729, 2976309}; // p, i
const uint32_t   current_control_PRESS[2] = {3456649, 10257}; // p, i

const uint32_t   pos_control_SLIDE[5] = {6933308, 139254287, 104848, 10219, 637}; // p, i, d, v, a
const uint32_t   pos_control_PICK[5] = {18462573, 157853228, 170004, 9945, 585}; // p, i, d, v, a //18462573, 157853228, 170004, 9945, 585
const uint32_t   pos_control_PRESS[5] = {200000, 905480, 2643, 507, 36}; // p, i, d, v, a

const float mm_to_enc_conversion_factor = 9.4;


#endif // TUNE_H