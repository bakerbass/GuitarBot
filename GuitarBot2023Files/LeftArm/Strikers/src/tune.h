#ifndef TUNE_H
#define TUNE_H

// strikerController.h
const float start_state_PICK[3] = {8, 4, 6}; // Picker encoder start position
const int   motor_id_PICK[3] = {13, 14, 15}; // maybe this goes in def...

// epos4.cpp
const int   home_offset_SLIDE = 50000; //52000
const int   home_offset_PRESS = -25;
const int   home_offset_PICK  = 0;

#endif // TUNE_H