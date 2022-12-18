import numpy as np
import pybullet as p
import yaml

# Constants
n_steps = 300

# Allcoate space for logging
n_vals = int(n_steps / 4)
pos = np.zeros((3, n_vals))
orientation = np.zeros((4, n_vals))
time = np.zeros(n_vals)

# Create pybullet instance
physicsClient = p.connect(p.DIRECT)  # or p.GUI for graphical version

# Setup gravity and objects
p.setGravity(0, 0, -9.81)

startPos = [0, 0, 3]
startOrientation = p.getQuaternionFromEuler([0, 0, 0])
sphereId = p.loadURDF("sphere.urdf", startPos, startOrientation)

rampId = p.loadURDF("Ramp.urdf", useFixedBase=True)

# Run the sim and log data of the sphere
k = 0
for i in range(300):
    p.stepSimulation()
    pos_t, orientation_t = p.getBasePositionAndOrientation(sphereId)
    if not i % 4:
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
orientation = orientation[np.array([3, 1, 2, 0]), :]
data["OBJECTS"]["sphere"]["ANIMATIONS"]["position"] = [time_str, str(pos.flatten().tolist())]
data["OBJECTS"]["sphere"]["ANIMATIONS"]["quaternion"] = [
    time_str,
    str(orientation.flatten().tolist()),
]

with open("ball_rolling.yaml", "w") as f:
    yaml.dump(data, f)
