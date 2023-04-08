import yaml
from scipy import integrate
import numpy as np

# Constants
f1_p = np.array([1.0, 1.0, 1.0])  # WRT inertial
f1_q = np.array([0.0, 0.0, 0.0, 1.0])
f1_v = np.array([1.0, 0.0, 0.0])  # WRT inertial
f1_w = np.array([0.0, 0.0, 1.0])  # WRT inertial

f2_p = np.array([1.0, 1.0, 1.0])  # WRT f1
f2_q = np.array([0.0, 0.0, 0.0, 1.0])
f2_v = np.array([0.2, 0.4, 0.3])  # WRT f1
f2_w = np.array([0.1, 0.5, -0.3])  # WRT f1

t = [0.0, 10.0]
dt = 1.0 / 30.0
n_steps = int((t[1] - t[0]) / dt) - 1

# Calculated
f2_v = f2_v + np.cross(f1_w, f2_p)  # WRT inertial
f2_w = f1_w + f2_w  # WRT inertial
f2_p = f1_p + f2_p  # WRT inertial

# Integrate and record position
S = np.hstack([f1_p, f1_q, f2_p, f2_q, f1_v, f1_w, f2_v, f2_w])


def wMat(w):
    return np.array(
        [
            [0.0, w[2], -w[1], w[0]],
            [-w[2], 0.0, w[0], w[1]],
            [w[1], -w[0], 0.0, w[2]],
            [-w[0], -w[1], -w[2], 0.0],
        ]
    )


def dS(S, _):
    dS = np.zeros_like(S)

    f1_q = S[3:7]
    f2_q = S[10:14]
    f1_v = S[14:17]
    f1_w = S[17:20]
    f2_v = S[20:23]
    f2_w = S[23:26]

    f1_q /= np.linalg.norm(f1_q)
    f2_q /= np.linalg.norm(f2_q)

    dS[0:3] = f1_v
    dS[3:7] = np.dot(wMat(f1_w), f1_q)
    dS[7:10] = f2_v
    dS[10:14] = np.dot(wMat(f2_w), f2_q)

    return dS


# Allocate memory and record initial position
rec = {
    "t": np.zeros(n_steps + 1),
    "f1_p": np.zeros((3, n_steps + 1)),
    "f1_q": np.zeros((4, n_steps + 1)),
    "f2_p": np.zeros((3, n_steps + 1)),
    "f2_q": np.zeros((4, n_steps + 1)),
}
rec["t"][0] = t[0]
rec["f1_p"][:, 0] = S[0:3]
rec["f2_p"][:, 0] = S[7:10]
rec["f1_q"][:, 0] = S[3:7]
rec["f2_q"][:, 0] = S[10:14]

# Time array
t = np.array([t[0], t[0] + dt])

# Integrate and record
for k in range(n_steps):
    S = integrate.odeint(dS, S, t)[1, :]

    f1_p = S[0:3]
    f1_q = S[3:7]
    f2_p = S[7:10]
    f2_q = S[10:14]

    f1_q /= np.linalg.norm(f1_q)
    f2_q /= np.linalg.norm(f2_q)

    S[3:7] = f1_q
    S[10:14] = f2_q

    rec["t"][k + 1] = t[1]
    rec["f1_p"][:, k + 1] = f1_p
    rec["f2_p"][:, k + 1] = f2_p
    rec["f1_q"][:, k + 1] = f1_q
    rec["f2_q"][:, k + 1] = f2_q

    t += dt

# Print to yaml file
with open("ktt.yaml.in", "r") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

time_str = str(rec["t"].tolist())

data["OBJECTS"]["f1"]["ANIMATIONS"]["position"] = [
    time_str,
    str(rec["f1_p"].transpose().flatten().tolist()),
]
data["OBJECTS"]["f1"]["ANIMATIONS"]["quaternion"] = [
    time_str,
    str(rec["f1_q"].transpose().flatten().tolist()),
]
data["OBJECTS"]["f2"]["ANIMATIONS"]["position"] = [
    time_str,
    str(rec["f2_p"].transpose().flatten().tolist()),
]
data["OBJECTS"]["f2"]["ANIMATIONS"]["quaternion"] = [
    time_str,
    str(rec["f2_q"].transpose().flatten().tolist()),
]

with open("ktt.yaml", "w") as f:
    yaml.dump(data, f)
