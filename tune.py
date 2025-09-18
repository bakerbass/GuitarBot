# tune.py
# Description: This file contains tunable parameters for the GuitarBotParser.
# Adjust these variables to fine-tune the robot's performance, physical calibration, and musical expression.

# ----------------------------------------------------------------------------
# 1. Trajectory and Interpolation Parameters
# ----------------------------------------------------------------------------
# These variables control the shape, speed, and timing of motor movements.
# For each trajectory value, multiply it by 5 to get the duration of the movement in milliseconds.
# For example, 10 points = 50ms to do the movement.

TIME_STEP = .005

#Graphing
# Controls graphing the functions used on each motor. False turns off, true turns on.
graph = False

# Blend percentage for trajectory interpolation (0.0 to 1.0).
# A higher value creates a more gradual acceleration and deceleration.
TRAJECTORY_BLEND_PERCENT = 0.2

# Initial Point
# Controls the starting point for the very first message sent to GuitarBot when the receiver file starts.
initial_point = [0, 0, 0, 0, 0, 0, -10, -10, -10, -10, -10, -10, 838, 937, 1450]


# Number of interpolation points for presser movements (e.g., pressing/unpressing).
# More points result in a slower movement.
PRESSER_INTERPOLATION_POINTS = 10

# Number of interpolation points for the main sliding motion of the left hand.
LH_SLIDER_MOTION_POINTS = 40

# Number of interpolation points when the left hand is moving to a single note.
LH_SINGLE_NOTE_MOTION_POINTS = 60

# Number of interpolation points for a single pluck.
PICKER_PLUCK_MOTION_POINTS = 11

# Position value for a fully unpressed left-hand presser motor.
LH_PRESSER_UNPRESSED_POS = -650

# Position value for a fully pressed left-hand presser motor.
LH_PRESSER_PRESSED_POS = 500

# Torque value for a press, used for sliding to ensure string contact.
# Given in terms of LH_PRESSER_SLIDE_PRESS_POS/1000 % of torque rating. For example, LH_PRESSER_SLIDE_PRESS_POS = 650 then the motor is outputting 65% of the motors' rated torque value.
# Values over 1000 overwork the motor, which can result in overheating and stalling.
LH_PRESSER_SLIDE_PRESS_POS = 400

# ----------------------------------------------------------------------------
# 2. Timing and Synchronization Parameters
# ----------------------------------------------------------------------------
# These variables control delays between actions and thresholds for interpreting MIDI data.

# Time (in seconds) the left hand needs to prepare before a picker plucks a new note.
# This ensures the fretting hand is in position before the string is struck.
# Given in terms of seconds.
LH_PREP_TIME_BEFORE_PICK = 0.400

# The time window (in seconds) to check for overlaps between left-hand and picker movements.
# If a pick event occurs within this window of a left-hand event, it may be adjusted or ignored.
# Given in terms of seconds.
MOVEMENT_OVERLAP_WINDOW = 0.300

# The duration (in seconds) below which a MIDI note is considered a single "pluck"
# rather than the start of a "tremolo".
# Given in terms of seconds.
TREMOLO_DURATION_THRESHOLD = 0.500

# The default duration (in seconds) assigned to very short notes to ensure they are played.
SHORT_NOTE_DEFAULT_DURATION = 0.025

# Timestamp rounding factor. Formats the floats to be in terms of 5 ms.
TIMESTAMP_ROUNDING_FACTOR = 200.0

# ----------------------------------------------------------------------------
# 3. Left Hand (LH) Physical Parameters
# ----------------------------------------------------------------------------
# Calibration values that map musical concepts (frets) to physical robot positions (mm, encoder ticks).

# The physical distance (in mm) from the nut to the center of each fret.
# Controls where the slider lands for fret 1, fret 2, fret 3, etc. respectively.
# Index 0 corresponds to Fret 1.
SLIDER_MM_PER_FRET = [17, 52, 87, 114, 141, 165, 188, 212, 234]

# Position values for the three states of the presser motors:
# 1: Open/Unpressed, 2: Pressed, 3: Muted (partially pressed).
PRESSER_ENCODER_POSITIONS = [-500, 650, 100]

# Conversion factor from millimeters to encoder ticks for the slider motors.
# Generally only needs to change if the motor is not Maxxon
# If you know the distance in mm and the encoder resolution of the motor, you can convert it directly to encoder ticks for that motor.
# Formula: (mm * ENCODER_RESOLUTION) / MM_PER_REVOLUTION
MM_TO_ENCODER_CONVERSION_FACTOR = 9.4

# An offset (in encoder ticks) applied to all slider motor calculations.
# Offsets the positions relative to the nut
SLIDER_ENCODER_OFFSET = -2000

# Multiplier to reverse the direction of specific slider motors if they are mounted mirrored.
# A value of -1 reverses the motor, 1 keeps it the same.
# Index corresponds to motor ID (String 1 = 0, String 2 = 1, etc.).
SLIDER_MOTOR_DIRECTION = [-1, 1, 1, -1, -1, 1]

# ----------------------------------------------------------------------------
# 4. Right Hand (RH) / Picker Physical Parameters
# ----------------------------------------------------------------------------
# Calibration values for the picking mechanism.

# Picker motor information: [down_pluck_mm, up_pluck_mm, encoder_resolution].
# Calibrate the mm positions for the desired picking depth and tone.
# Key is the motor ID.
PICKER_MOTOR_INFO = {
    0: {'down_pluck_mm': 4.3, 'up_pluck_mm': 7.3, 'resolution': 1024}, # E
    1: {'down_pluck_mm': 2.1, 'up_pluck_mm': 5.4, 'resolution': 2048}, # D
    2: {'down_pluck_mm': 3.6, 'up_pluck_mm': 6.6, 'resolution': 2048} # B
    # Add entries for other pickers if they exist, e.g., 3, 4, 5
}

# ----------------------------------------------------------------------------
# 5. Note and Chord Definitions
# ----------------------------------------------------------------------------
# Defines the mapping of MIDI notes to guitar strings.

# MIDI note ranges for each string/picker.
# Format: (lowest_note, highest_note, slider_direction_multiplier)
# The multiplier is used to account for mirrored slider mechanisms relative to the picker.
STRING_MIDI_RANGES = [
    (40, 49, SLIDER_MOTOR_DIRECTION[0]),  # String 1 (e.g., Low E for prototype)
    (50, 58, SLIDER_MOTOR_DIRECTION[2]),  # String 3 (e.g., D for prototype)
    (59, 68, SLIDER_MOTOR_DIRECTION[4]),  # String 5 (e.g., B for prototype)
    # Add other strings if applicable
    # (45, 55, 1),  # String 2
    # (55, 65, -1), # String 4
    # (64, 74, 1)   # String 6
]

# Filepath for the chord voicing library.
CHORD_LIBRARY_FILE = "Alternate_Chords.csv"

