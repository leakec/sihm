import numpy as np
from numpy.typing import NDArray
from scipy import integrate

# Constants
mu_e = 1.0  # mu of Earth
mu_m = 0.01  # mu of Moon

a_m = 10.0  # Semi-major axis of moon
a_r = 1.0  # Starting orbit of the rocket

t = [0.0, 10.0]
dt = 1.0 / 30.0

# Calculated constants
T_m = 2 * np.pi * np.sqrt(a_m**3 / mu_e)  # Period of the moon
w_m = 2 * np.pi / T_m  # Rotational rate of moon around earth

n_steps = int((t[1] - t[0]) / dt) - 1


def pM(t: float) -> NDArray:
    return np.array([a_m * np.sin(w_m * t), a_m * np.cos(w_m * t), 0.0])


# Equation of motion
def dS(S, t):
    p = S[0:3]
    v = S[3:6]

    p_m = pM(t)

    r_r_m = p_m - p  # From rocket to Moon
    r_r_e = -p  # From rocket to Earth

    dS = np.zeros_like(S)
    dS[0:3] = v
    dS[3:6] = mu_e * r_r_e / np.linalg.norm(r_r_e) ** 3 + mu_m * r_r_m / np.linalg.norm(r_r_m) ** 3
    return dS


# Initial state (circular orbit)
S = np.zeros(6)
S[0] = a_r
S[5] = np.sqrt(mu_e / a_r)

t = np.array([t[0], t[0] + dt])

# Allocate memory
rec = {"t": np.zeros(n_steps + 1), "p_r": np.zeros((3, n_steps + 1))}

for k in range(n_steps):
    S = integrate.odeint(dS, S, t)[1, :]
    rec["t"][k + 1] = t[1]
    rec["p_r"][:, k + 1] = S[0:3]
    t += dt
