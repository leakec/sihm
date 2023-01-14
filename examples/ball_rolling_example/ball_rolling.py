import numpy as np
import pybullet as p
import yaml

# Constants
n_steps = 3 * 240
gui = False

# Allcoate space for logging
log_freq = 4
n_vals = int(n_steps / log_freq)
pos = np.zeros((3, n_vals))
orientation = np.zeros((4, n_vals))
time = np.zeros(n_vals)

# Create pybullet instance
if gui:
    physicsClient = p.connect(p.GUI)
else:
    physicsClient = p.connect(p.DIRECT)

# Setup gravity and objects
p.setGravity(0, 0, -9.81)

startPos = [1.0, 0, 6.5]
startOrientation = p.getQuaternionFromEuler([0, 0, 0])
sphereId = p.loadURDF("sphere.urdf", startPos, startOrientation)

startPos = [0, 0, 0]
startOrientation = p.getQuaternionFromEuler([0, 0, 0])
rampId = p.loadURDF("Ramp.urdf", startPos, startOrientation, useFixedBase=True)

# Run the sim and log data of the sphere
k = 0
if gui:
    from time import sleep
for i in range(n_steps):
    p.stepSimulation()
    if gui:
        sleep(0.01)
    (
        pos_t,
        orientation_t,
    ) = p.getBasePositionAndOrientation(sphereId)
    if not i % log_freq:
        time[k] = i / 240.0
        pos[:, k] = pos_t
        orientation[:, k] = orientation_t
        k += 1

# Stop the sim
p.disconnect()

# Create the sihm file
import yaml

with open("ball_rolling.yaml.in", "r") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

time_str = str(time.tolist())
data["OBJECTS"]["sphere"]["ANIMATIONS"]["position"] = [
    time_str,
    str(pos.transpose().flatten().tolist()),
]
data["OBJECTS"]["sphere"]["ANIMATIONS"]["quaternion"] = [
    time_str,
    str(orientation.transpose().flatten().tolist()),
]

with open("ball_rolling.yaml", "w") as f:
    yaml.dump(data, f)
