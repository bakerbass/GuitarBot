import numpy as np
import matplotlib.pyplot as plt
from parsing.chord_selector import find_lowest_cost_chord


class ArmListParser:
    current_fret_positions = [0, 0, 0, 0, 0, 0]  # begins by preferring voicings near first position

    @staticmethod
    def _get_chords_M(filepath, chord_letter, chord_type):
        # print("chord stats: ", chord_type, chord_letter)
        fret_numbers_optimized = find_lowest_cost_chord(ArmListParser.current_fret_positions, filepath, chord_letter,
                                                        chord_type)
        ArmListParser.current_fret_positions = fret_numbers_optimized

        # NOTE keep for future use (when we want to know exactly which strings to strum)
        dtraj, utraj = [], []

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

        print(fret_numbers, fret_play)
        print(dtraj, utraj)

        return fret_numbers, fret_play, dtraj, utraj

    # parse right arm (strums) input
    @staticmethod
    def parseright_M(right_arm, measure_time):
        initialStrum = "D"
        firstbfound = False
        mra = 0
        pmra = 0
        pbra = 0
        deltaT = 0
        strumOnsets = []
        time = 0
        right_information = right_arm.copy()
        # print("right arm, parseright: ",right_arm)
        for measure in right_information:
            tempM = []
            bra = 0
            for beat in measure:
                # convert any lowercase inputs to uppercase:
                beat = str.upper(beat)

                if beat == "U" or beat == "D" or beat == "":
                    if not firstbfound:
                        if beat == "D":
                            strumOnsets.append([time, 'D', 'N'])
                            right_information[mra][bra] = [beat, "N", measure_time / 8, 1]  # Change strum time here
                        if beat == "U":
                            strumOnsets.append([time, 'U', 'N'])
                            right_information[mra][bra] = [beat, "N", measure_time / 8, 1]  # Change strum time here

                        firstbfound = True
                        initialStrum = beat
                        pmra = mra
                        pbra = bra

                        bra += 1
                        deltaT += measure_time / 8
                        time += measure_time / 8
                        checkfirst = False
                        continue
                    if beat == "U":
                        strumOnsets.append([time, 'U', 'N'])
                        right_information[mra][bra] = [beat, "N", measure_time / 8, deltaT]  # Change strum time here
                        if right_information[pmra][pbra][0] == "U":
                            right_information[pmra][pbra][1] = "C"
                        right_arm[pmra][pbra][3] = deltaT
                        pmra -= pmra
                        pmra += mra
                        pbra -= pbra
                        pbra += bra
                        deltaT = 0
                        # print(pmra, pbra)
                    if beat == "D":
                        strumOnsets.append([time, 'D', 'N'])
                        right_information[mra][bra] = [beat, "N", measure_time / 8, deltaT]  # Change strum time here
                        if right_information[pmra][pbra][0] == "D":
                            right_information[pmra][pbra][1] = "C"
                        right_information[pmra][pbra][3] = deltaT
                        pmra -= pmra
                        pmra += mra
                        pbra -= pbra
                        pbra += bra
                        deltaT = 0
                else:
                    print(right_information, mra, bra)
                    raise Exception("Right Arm input incorrect")
                bra += 1
                time += (measure_time / 8)
                # print(right_information, mra, bra, "loop")
                deltaT += measure_time / 8
            mra += 1
        count = 0
        for x in strumOnsets:
            try:
                if x[1] == 'D' and strumOnsets[count + 1][1] == 'D':
                    x[2] = 'C'
                if x[1] == 'U' and strumOnsets[count + 1][1] == 'U':
                    x[2] = 'C'
                count += 1
            except:
                break
        rh_events = []
        for x in strumOnsets:
            pos = 45
            if (x[1] == 'U'):
                pos = -45
            rh_events.append(['strum', pos, round(x[0], 3)])
        # print("ri", right_information, initialStrum)
        print("These are the strumOnsets: ", strumOnsets)
        print("These are the right hand events: ", rh_events)
        return rh_events, initialStrum, strumOnsets

    # parse left arm (chords) input
    @staticmethod
    def parseleft_M(left_arm, measure_time):
        firstc = []
        firstcfound = False
        mcount = 0
        mtimings = []
        time = 0
        for measure in left_arm:
            bcount = 0
            for chords in measure:
                if len(chords) != 0:
                    # Parse each individual chord input
                    # default to major, natural chord: 'C', 'G', 'F', etc.
                    key = 'n'
                    type = "MAJOR"

                    # in case the user entered a basic chord (ex. 'C'), we skip over this. Key/type have already been set by default
                    if len(chords) > 1:
                        curr_index = 1

                        # determine whether chord is sharp/natural/flat
                        key = chords[curr_index]
                        if key != '#' and key != 'b':
                            key = 'n'
                        else:
                            curr_index += 1

                        # grab the rest of the chord input
                        remaining_input = chords[curr_index:]

                        # check one-letter notations first
                        if len(remaining_input) == 1:
                            if remaining_input == 'm':
                                type = "MINOR"
                                # print("MINOR CHORD")

                            # TODO: split these into individual chords once chords library is updated
                            elif remaining_input == '7' or remaining_input == '9' or remaining_input == '13':
                                type = "DOMINANT"
                                # print("DOMINANT CHORD")
                            elif remaining_input == 'o':
                                type = "HALF-DIM"
                                # print("HALF-DIM CHORD")

                            # # TODO: add this to chords library, then uncomment
                            # elif remaining_input == '+':
                            #     type = "AUGMENTED"
                            #     # print("AUGMENTED CHORD")

                            elif remaining_input == '5':
                                type = "FIFTH"
                                # Power chord
                                # print("FIFTH CHORD")

                        # check two-letter notations
                        elif len(remaining_input) == 2:
                            if remaining_input == "M6":
                                type = "MAJOR6"
                                # print("MAJOR6 CHORD")
                            elif remaining_input == "M7":
                                type = "MAJOR7"
                                # print("MAJOR7 CHORD")
                            elif remaining_input == "M9":
                                type = "MAJOR9"
                                # print("MAJOR9 CHORD")
                            elif remaining_input == "m6":
                                type = "MINOR6"
                                # print("MINOR6 CHORD")
                            elif remaining_input == "m7":
                                type = "MINOR7"
                                # print("MINOR7 CHORD")
                            elif remaining_input == "m9":
                                type = "MINOR9"
                                # print("MINOR9 CHORD")

                            # # TODO: uncomment once added to chords library
                            # elif remaining_input == "m11":
                            #     type = "MINOR11"
                            #     # print("MINOR11 CHORD")

                        # check three-letter+ notations
                        elif len(remaining_input) >= 3:
                            if remaining_input == "sus" or remaining_input == "sus4":
                                type = "SUS4"
                                # print("SUS4 CHORD")
                            elif remaining_input == "sus2":
                                type = "SUS2"
                                # print("SUS2 CHORD")

                            # TODO: split these into individual chords once chords library is updated
                            elif remaining_input == "dim" or remaining_input == "dim7":
                                type = "DIMINISHED"
                                # print("DIMINISHED CHORD")

                            # check for test chord inputs
                            if remaining_input == "TEST0" or remaining_input == "TEST":
                                type = "TEST0"
                                print("test 0 accepted")
                            if remaining_input == "TEST1":
                                type = "TEST1"
                                print("test 1 accepted")
                            if remaining_input == "TEST2":
                                type = "TEST2"
                                print("test 2 accepted")
                            if remaining_input == "TEST3":
                                type = "TEST3"
                                print("test 3 accepted")
                            if remaining_input == "TEST4":
                                type = "TEST4"
                                print("test 4 accepted")
                            if remaining_input == "TEST5":
                                type = "TEST5"
                                print("test 5 accepted")
                            if remaining_input == "TEST6":
                                type = "TEST6"
                                print("test 6 accepted")
                            if remaining_input == "TEST7":
                                type = "TEST7"
                                print("test 7 accepted")

                    # read chord from csv
                    note = str.upper(chords[0])
                    # frets, command, dtraj, utraj = ArmListParser._get_chords_M("Chords - Chords.csv", note + key, type)
                    frets, command, dtraj, utraj = ArmListParser._get_chords_M("Alternate_Chords.csv", note + key, type)
                    left_arm[mcount][bcount] = [frets, command]
                    mtimings.append(time)
                    if not firstcfound:
                        firstc.append(frets)
                        firstc.append(command)
                        firstcfound = True
                time += measure_time / 4
                bcount += 1
            mcount += 1
        print("queue: ", mtimings)
        # print(left_arm)
        justchords = []
        lh_events = []
        i = 0
        for m in left_arm:
            for b in m:
                if b == '':
                    continue
                else:
                    justchords.append(b)
                    lh_events.append(["LH", b, round(mtimings[i], 3)])
                    i += 1
        # print("jc", justchords)
        print("These are the chord change onsets: ", mtimings)
        print("These are the LH Events: ", lh_events)
        # Note, lh_events is the new list we'd like to return.
        # Plan for LH Conversions to points
        # For each event, we want to send n x [[m], timestamp] where n is the number of points for an event and m are the 18 motor values.
        # STEP 1: convert to encoder tick positions.
        # For events in lh_events
        motor_positions = []
        slider_encoder_values = [43, 74, 105, 131, 163, 187, 210, 233, 255]
        presser_encoder_values = [-10, 38, 23]
        for events in lh_events:
            # for lh_events[1][0] AND for lh_events[1][1]
            # convert from fret position/finger position to encoder tick position respectively
            temp = [[]]
            for i, slider_value in enumerate(events[1][0]):
                if 1 <= slider_value <= 9:
                    temp[0].append(slider_encoder_values[slider_value - 1])
            for i, presser_value in enumerate(events[1][1]):
                if 1 <= presser_value <= 3:
                    temp[0].append(presser_encoder_values[presser_value - 1])
            temp.append(events[2])
            motor_positions.append(temp)

        # STEP 2: For every event, create a new list of points that interpolates between events.
        #

        # Generate the interpolated list
        interpolated_list = ArmListParser.generate_interpolated_positions(motor_positions, plot=True)

        # Print the result
        for entry in interpolated_list:
            print(f"Interpolated Points: {entry[0]}")
            print(f"Timestamp: {entry[1]}\n")

        print("These are the encoder tick slider/presser positions: ", motor_positions)
        # return left_arm, firstc, mtimings
        return lh_events, firstc, mtimings

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

        return curve

    @staticmethod
    def generate_interpolated_positions(motor_positions, num_points=20, tb_cent=0.2, plot=False):
        current_position = [43, 43, 43, 43, 43, 43]  # Initial position, remember to make dynamic later.
        result = []

        for event_index, event in enumerate(motor_positions):
            target_positions = event[0][:6]  # First 6 values of the nested list
            timestamp = event[1]

            interpolated_values = [
                ArmListParser.interp_with_blend(current_position[i], target_positions[i], num_points, tb_cent)
                for i in range(len(current_position))
            ]

            interpolated_points = list(map(list, zip(*interpolated_values)))

            result.append([interpolated_points, timestamp])

            if plot:
                ArmListParser.plot_interpolation(interpolated_values, event_index, timestamp)

            current_position = target_positions

        return result
    @staticmethod
    def plot_interpolation(interpolated_values, event_index, timestamp):
        plt.figure(figsize=(12, 8))
        for i, values in enumerate(interpolated_values):
            plt.plot(values, label=f'Point {i + 1}')

        plt.title(f'Interpolation for Event {event_index} (Timestamp: {timestamp})')
        plt.xlabel('Interpolation Step')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True)
        plt.show()


