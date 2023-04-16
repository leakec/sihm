import numpy as np
from numpy.typing import NDArray
from scipy import integrate

# Constants
mu_e = 1.0  # mu of Earth
mu_m = 0.01  # mu of Moon

a_m = 10.0  # Semi-major axis of moon
a_r = 1.0  # Starting orbit of the rocket
a_f = 0.5

dt = 1.0 / 30.0

# Calculated constants
T_m = 2 * np.pi * np.sqrt(a_m**3 / mu_e)  # Period of the moon
w_m = 2 * np.pi / T_m  # Rotational rate of moon around earth

T_r = 2 * np.pi * np.sqrt(a_r**3 / mu_e)  # Period of the rocket
a_d = a_m / 2.0 + a_r / 2.0 - a_f / 2.0  # Desired semi-major axis for transfer ellipse
T_d = 2 * np.pi * np.sqrt(a_d**3 / mu_e)  # Period of the transfer ellipse

v_d_p = np.sqrt(mu_e * (2 / a_r - 1 / a_d))  # Desired velocity for transfer
v_r = np.sqrt(mu_e / a_r)  # Initial velocity of the orbit
dv_1 = v_d_p - v_r  # Delta v for transfer ellipse

v_d_a = np.sqrt(mu_m * (2 / a_f - 1 / a_d))  # Velocity when coming in on transfer ellipse
v_f = -np.sqrt(mu_m / a_f)  # Desired final velocity
T_f = 2 * np.pi * np.sqrt(a_f**3 / mu_m)  # Final orbit period

# Figure out times
t_rel = [0.0, 2.0 * T_r, T_d / 2.0, T_f]  # Times of movements (relative to previous time)
t = np.zeros_like(t_rel)  # Times of movements (absolute)
for k in range(1, len(t_rel)):
    t[k] = t_rel[k] + t[k - 1]
n_steps_tot = int((t[-1] - t[0]) / dt)  # One extra since we will go one past the final step

# Moon positions over time
theta_m = np.pi - t[2] * w_m


def pM(t: float) -> NDArray:
    return np.array([a_m * np.cos(theta_m + w_m * t), a_m * np.sin(theta_m + w_m * t), 0.0])


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
S[4] = np.sqrt(mu_e / a_r)

t_int = np.array([t[0], t[0] + dt])

# Allocate memory
rec = {"t": np.zeros(n_steps_tot + 1), "p_r": np.zeros((3, n_steps_tot + 1))}
rec["p_r"][:, 0] = S[0:3]

# Initial orbit
k = 1
while t_int[1] < t[1]:
    S = integrate.odeint(dS, S, t_int)[1, :]
    rec["t"][k] = t_int[1]
    rec["p_r"][:, k] = S[0:3]
    t_int += dt
    k += 1
S[4] += dv_1
while t_int[1] < t[2]:
    S = integrate.odeint(dS, S, t_int)[1, :]
    rec["t"][k] = t_int[1]
    rec["p_r"][:, k] = S[0:3]
    t_int += dt
    k += 1
while t_int[1] < t[3]:
    S = integrate.odeint(dS, S, t_int)[1, :]
    rec["t"][k] = t_int[1]
    rec["p_r"][:, k] = S[0:3]
    t_int += dt
    k += 1

p_m = np.zeros_like(rec["p_r"])
for k, t in enumerate(rec["t"]):
    p_m[:, k] = pM(t)

# Check answers
if False:
    p_m = np.zeros_like(rec["p_r"])
    for k, t in enumerate(rec["t"]):
        p_m[:, k] = pM(t)
    from tfc.utils.PlotlyMakePlot import MakePlot

    p = MakePlot("x", "y", zlabs="z")
    p.Scatter3d(x=rec["p_r"][0, :], y=rec["p_r"][1, :], z=rec["p_r"][2, :], mode="lines")
    p.Scatter3d(x=p_m[0, :], y=p_m[1, :], z=p_m[2, :], mode="lines")
    p.fig["layout"]["scene"]["aspectmode"] = "cube"
    p.show()

# Create the sihm file
import yaml

with open("grav_assist.yaml.in", "r") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

time_str = str(rec["t"].tolist())
data["OBJECTS"]["moon"]["ANIMATIONS"]["position"] = [
    time_str,
    str(p_m.transpose().flatten().tolist()),
]
data["OBJECTS"]["rocket"]["ANIMATIONS"]["position"] = [
    time_str,
    str(rec["p_r"].transpose().flatten().tolist()),
]

with open("grav_assist.yaml", "w") as f:
    yaml.dump(data, f)
