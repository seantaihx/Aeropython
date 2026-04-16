import numpy as np
import math
import matplotlib.pyplot as plt


N = 50                                # Number of points in each direction
x_start, x_end = -2.0, 2.0            # x-direction boundaries
y_start, y_end = -1.0, 1.0            # y-direction boundaries
x = np.linspace(x_start, x_end, N)    # computes a 1D-array for x
y = np.linspace(y_start, y_end, N)    # computes a 1D-array for y
X, Y = np.meshgrid(x, y)              # generates a mesh grid

gamma = 5.0                      # strength of the vortex
x_vortex, y_vortex = 0.0, -0.3    # location of the vortex

def get_velocity_vortex(strength, xv, yv, X, Y):
    u = +strength / (2 * math.pi) * (Y - yv) / ((X - xv)**2 + (Y - yv)**2)
    v = -strength / (2 * math.pi) * (X - xv) / ((X - xv)**2 + (Y - yv)**2)
    return u, v


def get_stream_function_vortex(strength, xv, yv, X, Y):
    psi = strength / (4 * math.pi) * np.log((X - xv)**2 + (Y - yv)**2)
    return psi

# compute the velocity field on the mesh grid
u_vortex, v_vortex = get_velocity_vortex(gamma, x_vortex, y_vortex, X, Y)

# compute the stream-function on the mesh grid
psi_vortex = get_stream_function_vortex(gamma, x_vortex, y_vortex, X, Y)

# plot the streamlines
width = 10
height = (y_end - y_start) / (x_end - x_start) * width
speed = np.sqrt(u_vortex**2 + v_vortex**2)
speed = np.clip(speed, 0, 20)
speed = speed / 20
plt.figure(figsize=(width, height))
plt.xlabel('x', fontsize=16)
plt.ylabel('y', fontsize=16)
plt.xlim(x_start, x_end)
plt.ylim(y_start, y_end)
plt.streamplot(X, Y, u_vortex, v_vortex, color=speed, cmap='jet',
                  density=2, linewidth=1, arrowsize=1, arrowstyle='->')
plt.scatter(x_vortex, y_vortex, color='#CD2305', s=80, marker='o')
plt.tight_layout()
plt.savefig(f"vortex_g{gamma}.png", dpi=300)
plt.show()

strength_sink = 20.0            # strength of the sink
x_sink, y_sink = 0.25, -0.5       # location of the sink

def get_velocity_sink(strength, xs, ys, X, Y):
    u = strength / (2 * math.pi) * (X - xs) / ((X - xs)**2 + (Y - ys)**2)
    v = strength / (2 * math.pi) * (Y - ys) / ((X - xs)**2 + (Y - ys)**2)
    return u, v

def get_stream_function_sink(strength, xs, ys, X, Y):
    psi = strength / (2 * math.pi) * np.arctan2((Y - ys), (X - xs))
    return psi

# compute the velocity field on the mesh grid
u_sink, v_sink = get_velocity_sink(strength_sink, x_sink, y_sink, X, Y)

# compute the stream-function on the mesh grid
psi_sink = get_stream_function_sink(strength_sink, x_sink, y_sink, X, Y)

# superposition of the sink and the vortex
u = u_vortex + u_sink
v = v_vortex + v_sink
psi = psi_vortex + psi_sink

# plot the streamlines
width = 10
height = (y_end - y_start) / (x_end - x_start) * width
speed_sink = np.sqrt(u**2 + v**2)
speed_sink = np.clip(speed_sink, 0, 20)
speed_sink = speed_sink / 20
plt.figure(figsize=(width, height))
plt.xlabel('x', fontsize=16)
plt.ylabel('y', fontsize=16)
plt.xlim(x_start, x_end)
plt.ylim(y_start, y_end)
plt.streamplot(X, Y, u, v, color=speed_sink, cmap='jet', density=2, linewidth=1, arrowsize=1, arrowstyle='->')
plt.scatter(x_vortex, y_vortex, color='#CD2305', s=80, marker='o')
plt.scatter(x_sink, y_sink, color="green", s=80, marker='o')
plt.tight_layout()
plt.savefig(f"vortex_g{gamma}_s{strength_sink}_({x_sink},{y_sink}).png")
plt.show()
