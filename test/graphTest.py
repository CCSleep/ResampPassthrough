import numpy as np
import matplotlib.pyplot as plot

Pitch = [-173, -172, -171, -169, -167, -165, -161, -157, -151, -145, -137, -127, -116, -104, -91, -79, -66, -54, -44, -35, -27, -21, -16, -12, -9, -7, -5, -4, -3, -2, -1, -1, 0]
PBS1 = 0
PBS2 = 0
plot.title("OTO Simulator")
plot.xlabel("X Axis")
plot.ylabel("Y Axis")
plot.plot(np.arange(0+PBS1,len(Pitch)+PBS1), np.array([Pitch+PBS2 for Pitch in Pitch]), color="blue")
plot.show()
