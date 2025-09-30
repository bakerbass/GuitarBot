import numpy as np
import matplotlib.pyplot as plt
import math
from parsing.chord_selector import find_lowest_cost_chord
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import copy
import tune as tu


class GuitarBotParser:
    current_fret_positions = [0, 0, 0, 0, 0, 0]  # begins by preferring voicings near first position
    slide_toggle = None

    '''
        Main Dashboard Function
        Inputs: Raw chord, strum, pluck commands
        Outputs: Interpolated dictionary for RobotController to send to bot
    '''

    @staticmethod
    def parseAllMIDI(chords, pluck, initial_point, graph=tu.graph):
        # Initialize full dictionary
        allpoints = {}
        # Dictionaries for LH and RH

        # 1. Get events + Timestamps
        lh_motor_positions = GuitarBotParser.parseleftMIDI(chords)
        # rh_motor_positions, deflections = GuitarBotParser.parserightMIDI(strum) (dep)
        picker_motor_positions, slide_toggles = GuitarBotParser.parsePickMIDI(pluck)
        print("Slide Toggles: ", slide_toggles)

        # 2. PrepMovements (Adjust timestamps) LH changes occur before a strum,
        # lh_positions_adj, rh_positions_adj = GuitarBotParser.prepMovements(lh_motor_positions, rh_motor_positions) (dep)
        # Make sure no LH movements happen at the same time as a picker movement.
        picker_motor_positions_adj = GuitarBotParser.prepPicker(lh_motor_positions, picker_motor_positions)
        # print("LH events")
        # GuitarBotParser.print_Events(lh_positions_adj)
        # print("Picker events")
        # GuitarBotParser.print_Events(picker_motor_positions_adj)
        # 3. Interpolate (dedicated interp function)
        lh_dictionary, pick_dictionary = GuitarBotParser.interpolateEvents(lh_motor_positions,
                                                                           picker_motor_positions_adj,
                                                                           slide_toggles, initial_point)

        # print("Picker Dictionary: ")  # only up to 6
        # i = 0
        # for key, value in pick_dictionary.items():
        #     print(f"{i}| {key} : {value}")
        #     i += 1
        # Find the maximum timestamp across all dictionaries
        max_timestamp = max(max(lh_dictionary.keys()), max(pick_dictionary.keys()))
        print("Max Timestamp ParseAllMidi: ", max_timestamp)

        # Create a list of all timestamps, including interpolated ones
        all_timestamps = sorted(set(
            list(lh_dictionary.keys()) +
            # list(rh_dictionary.keys()) +
            list(pick_dictionary.keys()) +
            [round(t, 3) for t in np.arange(0, max_timestamp + tu.TIME_STEP, tu.TIME_STEP)]
        ))

        # Interpolate all dictionaries
        lh_interpolated = GuitarBotParser.interpolate_dict(lh_dictionary, all_timestamps)
        pick_interpolated = GuitarBotParser.interpolate_dict(pick_dictionary, all_timestamps)

        # Combine all dictionaries
        combined_dict = {}
        for timestamp in all_timestamps:
            combined_dict[timestamp] = (
                    lh_interpolated.get(timestamp, []) +
                    pick_interpolated.get(timestamp, [])
            )
        i = 0
        print("Full Matrix: ")
        for key, value in combined_dict.items():
            print(f"{i}| {key} : {value}")
            i += 1
        if graph:
            fig = go.Figure()

            # Add a trace for each motor
            for motor in range(15): # Change for number of motors
                # if motor > 13:
                y_values = [values[motor] for values in combined_dict.values()]
                fig.add_trace(
                    go.Scatter(x=list(combined_dict.keys()), y=y_values, mode='lines', name=f'Motor {motor + 1}'))

            # Update layout
            fig.update_layout(
                title='Motor Positions Over Time',
                xaxis_title='Timestamp',
                yaxis_title='Motor Position',
                legend_title='Motors'
            )

            # Show the plot
            fig.show()

        return combined_dict

    @staticmethod
    def _get_chords_M(filepath, chord_letter, chord_type):
        # print("chord stats: ", chord_type, chord_letter)

        fret_numbers_optimized = find_lowest_cost_chord(GuitarBotParser.current_fret_positions, filepath, chord_letter,
                                                        chord_type)
        GuitarBotParser.current_fret_positions = fret_numbers_optimized

        # NOTE Remove dtraj utraj stuff

        for i in range(6):
            if fret_numbers_optimized[i] != -1:
                dtraj = [i, 6]
                utraj = [6, i]
                break

        fret_numbers = fret_numbers_optimized.copy()
        fret_play = []

        # fret_play of 1 is open, 2 is pressed, 3 is muted
        for i in range(6):
            if fret_numbers[i] == 0:
                fret_numbers[i] = 1
                fret_play.append(1)
            elif fret_numbers[i] == -1:
                fret_numbers[i] = 1
                fret_play.append(3)
            else:
                fret_play.append(2)

        # print(fret_numbers, fret_play)
        # print(dtraj, utraj)

        return fret_numbers, fret_play, dtraj, utraj

    # This function creates a curve from q0 to qf with N points and smoothness of tb_cent of the curve.
    @staticmethod
    def interp_with_blend(q0, qf, N, tb_cent):
        curve = np.zeros(N)
        if curve is None:
            return
        nb = int(tb_cent * N)
        a_2 = 0.5 * (qf - q0) / (nb * (N - nb))

        for i in range(nb):
            tmp = a_2 * (i ** 2)
            curve[i] = q0 + tmp
            curve[N - i - 1] = qf - tmp

        tmp = a_2 * (nb ** 2)
        qa = q0 + tmp
        qb = qf - tmp

        curve[nb:N - nb] = np.linspace(qa, qb, N - (2 * nb))
        curve = curve.astype(int)

        return curve

    @staticmethod
    def lh_interpolate(lh_motor_positions, lh_pick_pos, initial_point, num_points=tu.PRESSER_INTERPOLATION_POINTS,
                       tb_cent=tu.TRAJECTORY_BLEND_PERCENT, plot=False):
        initial_point = initial_point[0:12]  # We only want the lh motors, sliders and pressers
        current_encoder_position = []
        sorted_lh_pick_pos = sorted(lh_pick_pos, key=lambda x: x[-1])

        # Determine the maximum timestamp to build a complete time range for the matrix
        if not lh_pick_pos:
            max_timestamp = lh_motor_positions[-1][1] + 0.6  # Creates placeholder if lh_pick_pos is empty
        else:
            max_timestamp = max(lh_motor_positions[-1][1] + 0.6, sorted_lh_pick_pos[-1][3] + .6)

        PLACEHOLDER_VALUE = 100000
        full_matrix = {}
        for t in np.arange(0, max_timestamp + tu.TIME_STEP, tu.TIME_STEP):
            # Initialize the matrix with placeholder values
            full_matrix[round(t, 3)] = [PLACEHOLDER_VALUE] * 12

        for i, value in enumerate(initial_point):
            current_encoder_position.append(value)

        print("LH UPDATED EVENTS LIST (NO SYNC LH EVENTS): ")
        lh_motor_positions = GuitarBotParser.checkSyncEvents("LH", lh_motor_positions)
        GuitarBotParser.print_Events(lh_motor_positions)

        # Combine chord and note events into a single chronological list
        full_LH = []
        for motor_pos, timestamp in lh_motor_positions:
            full_LH.append({'type': 'chord', 'positions': motor_pos, 'timestamp': timestamp})

        for motor_id, position, slide_toggle, timestamp in lh_pick_pos:
            full_LH.append(
                {'type': 'note', 'motor_id': motor_id, 'position': position, 'slide_toggle': slide_toggle,
                 'timestamp': timestamp})

        full_LH.sort(key=lambda x: x['timestamp'])

        # Set the starting position at time 0
        full_matrix[0] = initial_point
        prev_type = None
        prev_position = None
        prev_motor_id = None

        # --- Main Loop to Populate Trajectory ---
        for i, event in enumerate(full_LH):
            timestamp = round(event['timestamp'], 3)

            if timestamp in full_matrix:
                if event['type'] == 'chord':
                    # Generate a 3-part motion: UNPRESS -> SLIDE -> PRESS
                    points = []
                    target_positions_slider = event['positions'][:6]
                    target_positions_presser = event['positions'][6:12]
                    curr_pos = current_encoder_position.copy()

                    # 1. UNPRESS
                    interpolated_values_1 = [
                        GuitarBotParser.interp_with_blend(curr_pos[i], curr_pos[i], num_points, tb_cent) for i in
                        range(len(target_positions_slider))]
                    interpolated_points_1 = list(map(list, zip(*interpolated_values_1)))
                    interpolated_values_2 = [
                        GuitarBotParser.interp_with_blend(curr_pos[i + 6], tu.LH_PRESSER_UNPRESSED_POS, num_points,
                                                          tb_cent) for i in range(len(target_positions_presser))]
                    interpolated_points_2 = list(map(list, zip(*interpolated_values_2)))
                    f_20 = [points1 + points2 for points1, points2 in zip(interpolated_points_1, interpolated_points_2)]
                    points.extend(f_20)

                    # 2. SLIDE
                    interpolated_values_3 = [GuitarBotParser.interp_with_blend(curr_pos[i], target_positions_slider[i],
                                                                               tu.LH_SLIDER_MOTION_POINTS, tb_cent) for
                                             i in range(len(target_positions_slider))]
                    interpolated_points_3 = list(map(list, zip(*interpolated_values_3)))
                    interpolated_values_4 = [
                        GuitarBotParser.interp_with_blend(tu.LH_PRESSER_UNPRESSED_POS, tu.LH_PRESSER_UNPRESSED_POS,
                                                          tu.LH_SLIDER_MOTION_POINTS, tb_cent) for i in
                        range(len(target_positions_presser))]
                    interpolated_points_4 = list(map(list, zip(*interpolated_values_4)))
                    s_20 = [points1 + points2 for points1, points2 in zip(interpolated_points_3, interpolated_points_4)]
                    points.extend(s_20)

                    # 3. PRESS
                    interpolated_values_5 = [
                        GuitarBotParser.interp_with_blend(target_positions_slider[i], target_positions_slider[i],
                                                          num_points, tb_cent) for i in
                        range(len(target_positions_slider))]
                    interpolated_points_5 = list(map(list, zip(*interpolated_values_5)))
                    interpolated_values_6 = [
                        GuitarBotParser.interp_with_blend(tu.LH_PRESSER_UNPRESSED_POS, target_positions_presser[i],
                                                          num_points, tb_cent) for i in
                        range(len(target_positions_presser))]
                    interpolated_points_6 = list(map(list, zip(*interpolated_values_6)))
                    t_20 = [points1 + points2 for points1, points2 in zip(interpolated_points_5, interpolated_points_6)]
                    points.extend(t_20)

                    # Populate the full_matrix with the generated points
                    curr_t = timestamp
                    for curr_p in points:
                        full_matrix[curr_t] = curr_p
                        curr_t = round(curr_t + tu.TIME_STEP, 3)
                    current_encoder_position = copy.deepcopy(points[-1])

                elif event['type'] == 'note':
                    # Move a single finger for a note event
                    slider_points = []
                    presser_points = []
                    motor_index = event['motor_id']
                    slider_motor_ID = motor_index * 2
                    presser_motor_ID = motor_index * 2 + 6
                    q0_slider_motor = current_encoder_position[slider_motor_ID]
                    q0_presser_motor = current_encoder_position[presser_motor_ID]
                    qf_slider = int(event['position'])
                    qf_presser = tu.LH_PRESSER_PRESSED_POS
                    if int(event['position']) == -1:  # Open string case
                        qf_slider = q0_slider_motor
                        qf_presser = tu.LH_PRESSER_UNPRESSED_POS

                    if prev_type == 'chord' or not (
                            event['type'] == prev_type and prev_position == event['position'] and prev_motor_id ==
                            event['motor_id']):
                        if event['slide_toggle']:
                            s1 = GuitarBotParser.interp_with_blend(q0_slider_motor, q0_slider_motor, num_points,
                                                                   tb_cent)
                            p1 = GuitarBotParser.interp_with_blend(q0_presser_motor, tu.LH_PRESSER_SLIDE_PRESS_POS,
                                                                   num_points, tb_cent)
                            slider_points.extend(s1)
                            presser_points.extend(p1)

                            s2 = GuitarBotParser.interp_with_blend(q0_slider_motor, qf_slider,
                                                                   tu.LH_SINGLE_NOTE_MOTION_POINTS, tb_cent)
                            p2 = GuitarBotParser.interp_with_blend(tu.LH_PRESSER_SLIDE_PRESS_POS,
                                                                   tu.LH_PRESSER_SLIDE_PRESS_POS,
                                                                   tu.LH_SINGLE_NOTE_MOTION_POINTS, tb_cent)
                            slider_points.extend(s2)
                            presser_points.extend(p2)

                            s3 = GuitarBotParser.interp_with_blend(qf_slider, qf_slider, num_points, tb_cent)
                            p3 = GuitarBotParser.interp_with_blend(tu.LH_PRESSER_SLIDE_PRESS_POS, qf_presser,
                                                                   num_points, tb_cent)
                            slider_points.extend(s3)
                            presser_points.extend(p3)
                        else:  # Not a slide
                            s1 = GuitarBotParser.interp_with_blend(q0_slider_motor, q0_slider_motor, num_points, tb_cent)
                            p1 = GuitarBotParser.interp_with_blend(q0_presser_motor, tu.LH_PRESSER_UNPRESSED_POS, num_points,
                                                                   tb_cent)
                            slider_points.extend(s1)
                            presser_points.extend(p1)

                            s2 = GuitarBotParser.interp_with_blend(q0_slider_motor, qf_slider, tu.LH_SINGLE_NOTE_MOTION_POINTS, tb_cent)
                            p2 = GuitarBotParser.interp_with_blend(tu.LH_PRESSER_UNPRESSED_POS,
                                                                   tu.LH_PRESSER_UNPRESSED_POS, tu.LH_SINGLE_NOTE_MOTION_POINTS, tb_cent)
                            slider_points.extend(s2)
                            presser_points.extend(p2)

                            s3 = GuitarBotParser.interp_with_blend(qf_slider, qf_slider, num_points, tb_cent)
                            p3 = GuitarBotParser.interp_with_blend(tu.LH_PRESSER_UNPRESSED_POS, qf_presser, num_points, tb_cent)
                            slider_points.extend(s3)
                            presser_points.extend(p3)
                    else:  # Repeated note
                        s3 = GuitarBotParser.interp_with_blend(q0_slider_motor, qf_slider,
                                                               tu.LH_SINGLE_NOTE_MOTION_POINTS, tb_cent)
                        p3 = GuitarBotParser.interp_with_blend(q0_presser_motor, qf_presser, num_points, tb_cent)
                        slider_points.extend(s3);
                        presser_points.extend(p3)

                    # Populate the full_matrix with the generated points for the specific motors
                    curr_t = timestamp
                    for curr_p in slider_points:
                        full_matrix[curr_t][slider_motor_ID] = copy.deepcopy(curr_p)
                        curr_t = round(curr_t + tu.TIME_STEP, 3)
                    curr_t = timestamp
                    for curr_p in presser_points:
                        full_matrix[curr_t][presser_motor_ID] = copy.deepcopy(curr_p)
                        curr_t = round(curr_t + tu.TIME_STEP, 3)

                    current_encoder_position[slider_motor_ID] = s3[-1]
                    current_encoder_position[presser_motor_ID] = p3[-1]

                    prev_type = event["type"]
                    prev_position = event["position"]
                    prev_motor_id = event["motor_id"]

        last_known_values = initial_point.copy()
        for t in sorted(full_matrix.keys()):
            current_positions = full_matrix[t]
            for i in range(12):
                if current_positions[i] == PLACEHOLDER_VALUE:
                    current_positions[i] = last_known_values[i]
                else:
                    last_known_values[i] = current_positions[i]

        return full_matrix

    @staticmethod
    def print_Events(motor_positions):
        print("PRINTING EVENTS: ")
        for event in motor_positions:
            print(event)

    @staticmethod
    def print_Trajs(interpolated_list):
        print("INTERPOLATED LIST:")
        for e, event in enumerate(interpolated_list):
            print("Event: ", e)
            for traj in event:
                for i, points in enumerate(traj):
                    print(i, points)
                print("\n")

    @staticmethod
    def checkSyncEvents(event_type, motor_positions):
        prev_timestamp = -10000
        new_motor_positions = []
        for event in motor_positions:
            new_motor_positions.append(event)

        # Calculate total points for a full LH chord change trajectory
        lh_chord_change_points = (2 * tu.PRESSER_INTERPOLATION_POINTS) + tu.LH_SLIDER_MOTION_POINTS
        event_trajs = {
            "LH": lh_chord_change_points,
            "strum": 45,  # Strumming is deprecated but value is kept for now
            "pick": tu.PICKER_PLUCK_MOTION_POINTS
        }
        idx = 0
        for event_index, event in enumerate(motor_positions):
            points, timestamp = event
            delta = round(timestamp - prev_timestamp, 3)
            required_delta = event_trajs.get(event_type, 0) * tu.TIME_STEP
            if delta < required_delta:
                new_motor_positions.pop(idx)
                print(f"Not enough space between {event_type} events, ignoring event: ", idx)
                print("REQUIRED DELTA: ", required_delta)
                print(f"RESULTING DELTA: {timestamp} - {prev_timestamp} = {delta}")
                idx -= 1
            idx += 1
            prev_timestamp = timestamp
        return new_motor_positions

    @staticmethod
    def interpolateEvents(lh_positions_adj, picker_motor_positions_adj, slide_toggles, initial_point):
        pick_interpolated_dictionary, lh_pick_pos = GuitarBotParser.interpPick(picker_motor_positions_adj, slide_toggles,
                                                                               initial_point)
        lh_interpolated_dictionary = GuitarBotParser.lh_interpolate(lh_positions_adj, lh_pick_pos, initial_point,
                                                                      plot=False)

        return lh_interpolated_dictionary, pick_interpolated_dictionary

    @staticmethod
    def interpolate_dict(dictionary, all_timestamps):
        # print(dictionary)
        interpolated = {}
        last_value = None
        for timestamp in all_timestamps:
            if timestamp in dictionary:
                last_value = dictionary[timestamp]
            if last_value is not None:
                interpolated[timestamp] = last_value
        return interpolated

    @staticmethod
    def parse_chord(chords):
        key = 'n'
        chord_type = "MAJOR"
        if len(chords) > 1:
            curr_index = 1
            key = chords[curr_index]
            if key not in ['#', 'f']:
                key = 'n'
            else:
                curr_index += 1
            remaining_input = chords[curr_index:]
            if len(remaining_input) == 1:
                chord_types_one_letter = {'m': "MINOR", '7': "DOMINANT", '9': "DOMINANT", '13': "DOMINANT",
                                          'o': "HALF-DIM", '5': "FIFTH"}
                chord_type = chord_types_one_letter.get(remaining_input, chord_type)
            elif len(remaining_input) == 2:
                chord_types_two_letters = {"M6": "MAJOR6", "M7": "MAJOR7", "M9": "MAJOR9", "m6": "MINOR6",
                                           "m7": "MINOR7", "m9": "MINOR9"}
                chord_type = chord_types_two_letters.get(remaining_input, chord_type)
            elif len(remaining_input) >= 3:
                chord_types_three_letters = {"sus": "SUS4", "sus4": "SUS4", "sus2": "SUS2", "dim": "DIMINISHED",
                                             "dim7": "DIMINISHED"}
                chord_type = chord_types_three_letters.get(remaining_input, chord_type)
                if remaining_input.startswith("TEST"):
                    test_number = remaining_input[4:]
                    if test_number.isdigit():
                        chord_type = f"TEST{test_number}"
                        print(f"test {test_number} accepted")
        note = str.upper(chords[0])
        frets, command, dtraj, utraj = GuitarBotParser._get_chords_M(tu.CHORD_LIBRARY_FILE, note + key, chord_type)
        return frets, command, dtraj, utraj, note, key, chord_type

    @staticmethod
    def parseleftMIDI(chords):
        lh_events = []
        for curr_chord in chords:
            note = curr_chord[0][0]
            timestamp = curr_chord[1]
            timestamp = round(timestamp * tu.TIMESTAMP_ROUNDING_FACTOR) / tu.TIMESTAMP_ROUNDING_FACTOR

            chord_input = note + curr_chord[0][1:]
            frets, command, dtraj, utraj, parsed_note, key, chord_type = GuitarBotParser.parse_chord(chord_input)
            lh_events.append(["LH", [frets, command], timestamp])

        lh_motor_positions = []
        slider_encoder_values = []
        for value in tu.SLIDER_MM_PER_FRET:
            # 2048 is the encoder resolution of the sliders. This likely won't change.
            encoder_tick = (value * 2048) / tu.MM_TO_ENCODER_CONVERSION_FACTOR + tu.SLIDER_ENCODER_OFFSET
            slider_encoder_values.append(encoder_tick)

        for events in lh_events:
            temp = [[]]
            for i, slider_value in enumerate(events[1][0]):
                mult = tu.SLIDER_MOTOR_DIRECTION[i]
                if 1 <= slider_value <= len(slider_encoder_values):
                    temp[0].append(slider_encoder_values[slider_value - 1] * mult)
            for i, presser_value in enumerate(events[1][1]):
                if 1 <= presser_value <= len(tu.PRESSER_ENCODER_POSITIONS):
                    temp[0].append(tu.PRESSER_ENCODER_POSITIONS[presser_value - 1])
            temp.append(events[2])
            lh_motor_positions.append(temp)
        return lh_motor_positions

    @staticmethod
    def parsePickMIDI(picks):
        pick_events = []
        slide_toggles = []
        string_ranges_tuples = [(r[0], r[1]) for r in tu.STRING_MIDI_RANGES]

        active_pickers = [-.5] * len(string_ranges_tuples)
        last_notes = [None] * len(string_ranges_tuples)
        for note, duration, speed, slide_toggle, timestamp in picks:
            slide_toggles.append(slide_toggle)
            assigned = False
            timestamp = round(timestamp * tu.TIMESTAMP_ROUNDING_FACTOR) / tu.TIMESTAMP_ROUNDING_FACTOR
            duration = round(duration, 3)
            if duration < tu.TREMOLO_DURATION_THRESHOLD:
                duration = tu.SHORT_NOTE_DEFAULT_DURATION

            for pickerID, (low, high) in enumerate(string_ranges_tuples):
                if low <= note <= high:
                    if last_notes[pickerID] == note:
                        if timestamp >= active_pickers[pickerID]:
                            assigned = True
                    else:
                        single_note_prep_time = (20 + 25 + 20) * tu.TIME_STEP  # Corresponds to non-sliding note trajectory
                        if timestamp - single_note_prep_time >= active_pickers[pickerID]:
                            assigned = True
                    if assigned:
                        end = timestamp
                        pick_events.append(["pick", [pickerID, note, duration, speed, timestamp]])
                        active_pickers[pickerID] = end
                        last_notes[pickerID] = note
                        break
            if not assigned:
                print(f"Warning: No available picker for note {note} at timestamp {timestamp}")

        pick_motor_positions = []
        num_pickers = len(tu.PICKER_MOTOR_INFO)
        pickerStates = [1] * num_pickers
        for event in pick_events:
            motor_id, note, duration, speed, timestamp = event[1]
            timestamp = round(timestamp * tu.TIMESTAMP_ROUNDING_FACTOR) / tu.TIMESTAMP_ROUNDING_FACTOR
            curr_event = [motor_id, note, 0, duration, speed]
            lh_tmstmp = timestamp - tu.LH_PREP_TIME_BEFORE_PICK

            if duration < tu.TREMOLO_DURATION_THRESHOLD:
                pick_state = pickerStates[motor_id]
                destination_key = 'down_pluck_mm' if pick_state else 'up_pluck_mm'
                qf_mm = tu.PICKER_MOTOR_INFO[motor_id][destination_key]
                resolution = tu.PICKER_MOTOR_INFO[motor_id]['resolution']
                pos2pulse = (qf_mm * resolution) / tu.MM_TO_ENCODER_CONVERSION_FACTOR
                curr_event[2] = round(pos2pulse, 3)
                pickerStates[motor_id] = not pick_state
            else:
                pick_state = pickerStates[motor_id]
                destination_key = 'down_pluck_mm' if pick_state else 'up_pluck_mm'
                qf_mm = tu.PICKER_MOTOR_INFO[motor_id][destination_key]
                resolution = tu.PICKER_MOTOR_INFO[motor_id]['resolution']
                pos2pulse = (qf_mm * resolution) / tu.MM_TO_ENCODER_CONVERSION_FACTOR
                curr_event[2] = round(pos2pulse, 3)
            full_event = [curr_event, timestamp]
            pick_motor_positions.append(full_event)
        return pick_motor_positions, slide_toggles

    @staticmethod
    def prepPicker(lh_motor_positions, pick_motor_positions):
        pick_motor_positions_prepped = []
        lh_index = 0
        for pick_element in pick_motor_positions:
            pick_timestamp = pick_element[1]
            overlap = False
            while lh_index < len(lh_motor_positions) and lh_motor_positions[lh_index][1] <= pick_timestamp + tu.MOVEMENT_OVERLAP_WINDOW:
                lh_timestamp = lh_motor_positions[lh_index][1]
                if abs(pick_timestamp - lh_timestamp) <= tu.MOVEMENT_OVERLAP_WINDOW:
                    overlap = True
                    break
                lh_index += 1
            if not overlap:
                pick_motor_positions_prepped.append(pick_element)
        return pick_motor_positions_prepped

    @staticmethod
    def interpPick(pick_events, slide_toggles, initial_point, num_points=20, tb_cent=tu.TRAJECTORY_BLEND_PERCENT):
        initial_point = initial_point[12:]
        current_positions = initial_point.copy()
        result = {}
        # The 'pick_states' variable has been removed.
        events_list = []
        lh_pick_events = []

        for i, event in enumerate(pick_events):
            motor_id, note, qf_encoder_picker, duration, speed = event[0]
            is_pluck = duration < tu.TREMOLO_DURATION_THRESHOLD
            start_pos = current_positions[motor_id]

            # --- Common Setup for Both Pluck and Tremolo ---
            # Get encoder positions for up and down, as they are needed to determine the opposite point.
            down_mm = tu.PICKER_MOTOR_INFO[motor_id]['down_pluck_mm']
            up_mm = tu.PICKER_MOTOR_INFO[motor_id]['up_pluck_mm']
            resolution = tu.PICKER_MOTOR_INFO[motor_id]['resolution']
            down_encoder = (down_mm * resolution) / tu.MM_TO_ENCODER_CONVERSION_FACTOR
            up_encoder = (up_mm * resolution) / tu.MM_TO_ENCODER_CONVERSION_FACTOR

            # Determine the midpoint to decide if the current position is "up" or "down".
            mid_point = (up_encoder + down_encoder) / 2

            if is_pluck:
                destination_pos = down_encoder if start_pos > mid_point else up_encoder

                all_points = GuitarBotParser.interp_with_blend(start_pos, destination_pos,
                                                               tu.PICKER_PLUCK_MOTION_POINTS, tb_cent)
                events_list.append([all_points, motor_id, event[1]])
                current_positions[motor_id] = all_points[-1]
            else:
                # --- Tremolo Logic (Position-Based) ---
                fill_points = min(30, int(30 - (speed - 1) * (25 / 9))) - 4
                single_pick_duration = (fill_points * tu.TIME_STEP) + 0.055

                if single_pick_duration > 0:
                    num_picks = math.floor(duration / single_pick_duration)
                else:
                    num_picks = 0

                all_points = []
                current_pick_pos = start_pos
                num_motion_points = tu.PICKER_PLUCK_MOTION_POINTS

                for _ in range(num_picks):
                    destination_pos = down_encoder if current_pick_pos > mid_point else up_encoder
                    points1 = GuitarBotParser.interp_with_blend(current_pick_pos, destination_pos, num_motion_points,
                                                                .2)
                    points2 = GuitarBotParser.interp_with_sine_blend(destination_pos, destination_pos, fill_points)
                    all_points.extend(points1)
                    all_points.extend(points2)

                    current_pick_pos = destination_pos

                if all_points:
                    events_list.append([all_points, motor_id, event[1]])
                    current_positions[motor_id] = all_points[-1]
                else:
                    current_positions[motor_id] = start_pos

            # --- Remainder of the function (unchanged) ---
            fret = note - tu.STRING_MIDI_RANGES[motor_id][0]
            if fret == 0:
                lh_enc_val = -1
            else:
                slider_direction = tu.STRING_MIDI_RANGES[motor_id][2]
                lh_enc_val = ((tu.SLIDER_MM_PER_FRET[
                                   fret - 1] * 2048) / tu.MM_TO_ENCODER_CONVERSION_FACTOR + tu.SLIDER_ENCODER_OFFSET) * slider_direction
            curr_lhp_event = [motor_id, lh_enc_val, slide_toggles[i], event[1] - tu.LH_PREP_TIME_BEFORE_PICK]
            lh_pick_events.append(curr_lhp_event)

        max_timestamp = 0
        if events_list:
            for i, pick_event in enumerate(events_list):
                timestamp = pick_event[2]
                duration = tu.TIME_STEP * len(pick_event[0])
                event_time = round((timestamp + duration) * tu.TIMESTAMP_ROUNDING_FACTOR) / tu.TIMESTAMP_ROUNDING_FACTOR
                if event_time > max_timestamp:
                    max_timestamp = event_time

        curr_timestamp = 0
        while curr_timestamp <= max_timestamp:
            result[curr_timestamp] = initial_point.copy()
            curr_timestamp = round(curr_timestamp + tu.TIME_STEP, 3)
        for event in events_list:
            points, id, timestamp = event
            curr = round(timestamp * tu.TIMESTAMP_ROUNDING_FACTOR) / tu.TIMESTAMP_ROUNDING_FACTOR
            for p in points:
                result[curr][id] = p
                curr = round(curr + tu.TIME_STEP, 3)
                prev_pos = p
            while curr <= max_timestamp:
                result[curr][id] = prev_pos
                curr = round(curr + tu.TIME_STEP, 3)
        print("LH PICK EVENTS: ", lh_pick_events)
        return result, lh_pick_events

    @staticmethod
    def scale_speed(value):
        usermin, usermax = 1, 10
        fastest, slowest = 0.025, 0.15
        scaled = (10 + 2 * ((slowest / tu.TIME_STEP) - (value - 1) * ((fastest * 1000) / (usermax - usermin)))) * tu.TIME_STEP
        return scaled

    @staticmethod
    def tremolocos(curT, period, amp, vert_shift, pick_state):
        if pick_state == 1:
            tremolo_s = vert_shift + amp * math.cos((2 * math.pi * (curT)) / period)
        else:
            tremolo_s = vert_shift + amp * -math.cos((2 * math.pi * (curT)) / period)
        return tremolo_s

    @staticmethod
    def maketremolo(vert_shift, amp, duration, speed, pick_state):
        period = GuitarBotParser.scale_speed(speed)
        tstep = tu.TIME_STEP
        num_tremolos = (duration // period)
        trem_times = np.arange(0, (num_tremolos * period) + tstep, tstep)
        tremoloArray = [GuitarBotParser.tremolocos(t, period, amp, vert_shift, pick_state) for t in trem_times]
        end_fill = duration - trem_times[-1]
        fill_array = []
        if end_fill > 0:
            fill_array = np.full(int(period // tu.TIME_STEP),
                                 GuitarBotParser.tremolocos(trem_times[-1], period, amp, vert_shift, pick_state))
        tremoloArray.extend(fill_array)
        return tremoloArray

    @staticmethod
    def scaleAmplitude(max_amplitude, min_amplitude, speed):
        print("Max Amplitude, Min Amplitude: ", max_amplitude, min_amplitude)
        low_speed, high_speed = 1, 10
        scaledAmp = max_amplitude + ((speed - low_speed) / (high_speed - low_speed)) * (min_amplitude - max_amplitude)
        return scaledAmp

    @staticmethod
    def interp_with_sine_blend(start_pos, end_pos, num_points):
        t = np.linspace(0, np.pi, num_points)
        blend = (1 - np.cos(t)) / 2
        points = (1 - blend) * start_pos + blend * end_pos
        return points