import numpy as np
from matplotlib import pyplot as plt


def interpWithBend(q0, qf, N, tb_cent=0.2):
    nb = int(tb_cent * N)
    a_2 = 0.5 * (qf - q0) / (nb * (N - nb))

    curve = np.zeros(N, dtype=float)

    for i in range(nb):
        tmp = a_2 * pow(i, 2)
        curve[i] = q0 + tmp
        curve[N - i - 1] = qf - tmp

    tmp = a_2 * pow(nb, 2)
    qa = q0 + tmp
    qb = qf - tmp
    curve[nb: N - nb] = np.linspace(qa, qb, N - (2 * nb))

    return curve


def linearInterpolate(q0: float, qf: float, N: int, a: float, time_resolution: float):
    tf = N * time_resolution

    # a_2 = 0.5 * (qf - q0) / (Nb * (N - Nb))
    # (tb ** 2) - tb * tf + (qf - q0) / a = 0
    # D = tf**2 - (4 * (qf - q0) / a)
    # tb = (tf - np.sqrt(D)) / 2

    D = (tf**2) - 4*(qf - q0) / a
    assert D >= 0, "Not enough acceleration!"

    tb = (tf - np.sqrt(D)) / 2
    Nb = int(np.ceil(tb / time_resolution))
    y = np.zeros(N, dtype=float)

    for i in range(Nb):
        tmp = 0.5 * a * ((i * time_resolution)**2)
        y[i] = q0 + tmp
        y[N - i - 1] = qf - tmp

    tmp = 0.5 * a * (tb ** 2)
    qa = q0 + tmp
    qb = qf - tmp

    y[Nb: N - Nb] = np.linspace(qa, qb, N - 2*Nb)

    return y

# --------- My Code ------------

def deriveTwice(out, N):
    derive = np.gradient(out)
    derive2 = np.gradient(derive)
    return derive2
    # x_values = np.linspace(0, 1, 100)
    # x_final = N
    # y_final = np.interp(x_final, x_values, out)
    # y_initial = np.interp(0, x_values, out)


def optimization(e, a, d, g, b, e2, N):
    x_values = np.linspace(0, 1, N)
    x_final = N
    avg = x_final / 2
    strings = [e, a, d, g, b, e2]

    costs = [np.gradient(np.gradient(string)) for string in strings]
    y_values = [abs(np.interp(avg, x_values, cost)) for cost in costs]

    min_cost_string = np.argmin(y_values)
    return strings[min_cost_string]

# -----------------------------




