import numpy as np
import traj
import pandas as pd

def get_chords_M(directory, chord_letter, chord_type):
    df_chords = pd.read_csv(directory)
    chord_possibilities = []
    for new_x in range(334):
        if df_chords.iloc[new_x].iloc[0] == chord_letter:
            if df_chords.iloc[new_x].iloc[1] == chord_type:
                x = new_x
                chord = [df_chords.iloc[new_x].iloc[3], df_chords.iloc[new_x].iloc[4],
                    df_chords.iloc[new_x].iloc[5], df_chords.iloc[new_x].iloc[6],
                    df_chords.iloc[new_x].iloc[7], df_chords.iloc[new_x].iloc[8]]
                chord_possibilities.append(chord)

    return chord_possibilities


def calculate_cost(arr1, arr2, N = 25):
    cost = 0
    for a, b in zip(arr1, arr2):
        fret_lengths = [0, 35.63981144712466, 33.639502533759924,
                        31.751462333006657, 29.96938968620543, 28.287337091556935,
                        26.69969085488873, 25.201152354471787, 23.786720357363606,
                        22.45167432825832, 21.191558675138026]

        y1 = fret_lengths[a]
        y2 = fret_lengths[b]

        x_values = np.linspace(0, 1, N)
        avg = (0 + N) / 2

        out = traj.interpWithBend(y1, y2, 25, 0.2)
        costs = abs(np.gradient(out))
        y_value = np.interp(avg, x_values, costs)

        cost += y_value * 59.9406059


    return cost


def findLowestCostChord(current_fret_positions, directory, chord_letter, chord_type):
    min_cost = float('inf')
    easiest_frets = None

    for arr in get_chords_M(directory, chord_letter, chord_type):
        cost = calculate_cost(arr, current_fret_positions)
        if cost < min_cost:
            min_cost = cost
            easiest_frets = arr

    return easiest_frets
