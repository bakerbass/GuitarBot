import numpy as np
import traj
import notes


def optimization(current_fret_positions, current_string, desired_note, N = 25):
    desired_note = notes.notePossibilities(desired_note)
    fret_lengths = [0, 35.63981144712466, 33.639502533759924,
                    31.751462333006657, 29.96938968620543, 28.287337091556935,
                    26.69969085488873, 25.201152354471787, 23.786720357363606,
                    22.45167432825832, 21.191558675138026]
    fret_costs = []

    if desired_note == [-1, -1, -1, -1, -1, -1]:
        print("unplayable")
        return

    for string, current_fret in enumerate(current_fret_positions):
        if desired_note[string] == -1 and desired_note != [-1, -1, -1, -1, -1, -1]:
            fret_costs.append(10000)
        else:
            # abs(math.log(x + 12.3097, 0.964985) + 108.284)
            y1 = fret_lengths[current_fret_positions[string]]
            y2 = fret_lengths[desired_note[string]]

            x_values = np.linspace(0, 1, N)
            avg = (0 + N)/2

            out = traj.interpWithBend(y1, y2, 25, 0.2)
            costs = abs(np.gradient(out))
            y_value = np.interp(avg, x_values, costs)

            fret_costs.append(y_value * 59.9406059)

    string_costs = []

    for i in range(6):
        string_costs.append(abs(i - current_string))

    string_fret_costs = []

    j = 0
    for cost in fret_costs:
        string_fret_costs.append((0.8 * cost) + (0.2 * string_costs[j]))
        j += 1

    min_cost_string = np.argmin(string_fret_costs)

    new_string_pos = min_cost_string
    new_fret_pos = current_fret_positions
    new_fret_pos[min_cost_string] = desired_note[min_cost_string]

    return string_fret_costs, new_string_pos, new_fret_pos

