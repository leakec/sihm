import numpy as np
import pybullet as p
import yaml

# Constants
n_steps = 30 * 240
gui = False
p1_init_ang = np.pi/2
p2_init_ang = np.pi/4

# Allcoate space for logging
log_freq = 10 
n_vals = int(n_steps / log_freq)
pos = {"p1": np.zeros((3, n_vals)), "p2": np.zeros((3, n_vals))}
orientation = {"p1": np.zeros((4, n_vals)), "p2": np.zeros((4, n_vals))}
time = np.zeros(n_vals)

# Create pybullet instance
if gui:
    physicsClient = p.connect(p.GUI)
else:
    physicsClient = p.connect(p.DIRECT)

# Setup objects and gravity
startPos = [0.0, 0.0, 0.0]
startOrientation = p.getQuaternionFromEuler([0, 0, 0])
double_pendulum = p.loadURDF("double_pendulum.urdf", startPos, startOrientation)

p.resetJointState(double_pendulum, 0, p1_init_ang)
p.setJointMotorControl2(double_pendulum, 0, controlMode=p.VELOCITY_CONTROL, force=0)
p.changeDynamics(double_pendulum,0,linearDamping=0.0, angularDamping=0.0)

p.resetJointState(double_pendulum, 1, p2_init_ang)
p.setJointMotorControl2(double_pendulum, 1, controlMode=p.VELOCITY_CONTROL, force=0)
p.changeDynamics(double_pendulum,1,linearDamping=0.0, angularDamping=0.0)

#p.setCollisionFilterPair(double_pendulum, double_pendulum, 0, 1, 0)

p.setGravity(0, -9.81, 0)

# Run the sim and log data of the pendulums
k = 0
if gui:
    from time import sleep
for i in range(n_steps):
    p.stepSimulation()
    if gui:
        sleep(0.001)
    if not i % log_freq:
        time[k] = i / 240.0

        p1 = p.getLinkState(double_pendulum, 0)
        pos["p1"][:,k] = p1[4]
        orientation["p1"][:,k] = p1[5]

        p2 = p.getLinkState(double_pendulum, 1)
        pos["p2"][:,k] = p2[4]
        orientation["p2"][:,k] = p2[5]

        k += 1

# Stop the sim
#if not gui:
#    p.disconnect()

# Create the sihm file
import yaml

with open("double_pendulum.yaml.in", "r") as f:
    data = yaml.load(f, Loader=yaml.FullLoader)

time_str = str(time.tolist())
data["OBJECTS"]["pendulum_1"]["ANIMATIONS"]["position"] = [
    time_str,
    str(pos["p1"].transpose().flatten().tolist()),
]
data["OBJECTS"]["pendulum_1"]["ANIMATIONS"]["quaternion"] = [
    time_str,
    str(orientation["p1"].transpose().flatten().tolist()),
]
data["OBJECTS"]["pendulum_2"]["ANIMATIONS"]["position"] = [
    time_str,
    str(pos["p2"].transpose().flatten().tolist()),
]
data["OBJECTS"]["pendulum_2"]["ANIMATIONS"]["quaternion"] = [
    time_str,
    str(orientation["p2"].transpose().flatten().tolist()),
]

with open("double_pendulum.yaml", "w") as f:
    yaml.dump(data, f)
