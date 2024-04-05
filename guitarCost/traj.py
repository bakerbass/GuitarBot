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


# out = linearInterpolate(0, 2, 40, 8000, 0.001)

out = np.zeros(75, dtype=float)
# out[:25]    = interpWithBend(10, 5, 25, 0.3) # how fast it accelerates
# out[25:50]  = interpWithBend(5, -10, 25, 0.1)
# out[50:]    = interpWithBend(-10, 10, 25, 0.1)

# all of these graphs are different strings

# e = interpWithBend(-3, 5, 25, 0.3)
# e_derive = np.gradient(e)
# e_derive2 = np.gradient(np.gradient(e))
# a = interpWithBend(4, -10, 25, 0.3)
# a_derive = np.gradient(a)
# a_derive2 = np.gradient(np.gradient(a))
# new = interpWithBend(3, 8, 25, 0.1)
# new_derive = np.gradient(new)
# new_derive2 = np.gradient(new_derive)
# print(e_derive2, a_derive2, new_derive2)

# d = interpWithBend(0, 3, 25, 0.1)
# g = interpWithBend(6, 9, 25, 0.4)
# b = interpWithBend(2, -5, 25, 0.2)
# e2 = interpWithBend(0, 7, 25, 0.2)

# print(optimization(e, a, d, g, b, e2, 25))

# take og graph, derive twice, find average value.

out = np.zeros(75, dtype=float)
out[:25]    = interpWithBend(10, 5, 25, 0.3)
out[25:50]  = interpWithBend(5, -10, 25, 0.1)
out[50:]    = interpWithBend(-10, 10, 25, 0.1)

# what are the different ways i can play it
# make the trajectories

# plt.plot(e, label = 'e string')
# plt.plot(e_derive, label = 'e derive')
# plt.plot(e_derive2, label = 'e derive2')
# plt.plot(-(a), label = 'a string')
# plt.plot(-(a_derive), label = 'a derive')
# plt.plot(-(a_derive2), label = 'a derive2')
# plt.plot(new, label = 'new string')
# plt.plot(new_derive, label = 'new derive')
# plt.plot(new_derive2, label = 'new derive2')
# plt.plot(d, label = 'd string')
# plt.plot(g, label = 'g string')
# plt.plot(b, label = 'b string')
# plt.plot(e2, label = 'e2 string')
# plt.legend()
# plt.show()


