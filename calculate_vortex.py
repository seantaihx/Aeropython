import numpy as np
import matplotlib.pyplot as plt

def get_velocity_vortex(strength, xv, yv, x0, y0):

    u = +strength / (2 * np.pi) * (y0 - yv) / ((x0 - xv)**2 + (y0 - yv)**2)
    v = -strength / (2 * np.pi) * (x0 - xv) / ((x0 - xv)**2 + (y0 - yv)**2)
    
    return u, v


def get_next_pos(x0,y0,u,v,dt):
    
    x_next = x0 + u * dt
    y_next = y0 + v * dt
    
    return x_next, y_next

def get_velocity_sink(strength, xs, ys, x0, y0):
    u = -strength / (2 * np.pi) * (y0 - ys) / ((x0 - xs)**2 + (y0 - ys)**2)
    v = -strength / (2 * np.pi) * (x0 - xs) / ((x0 - xs)**2 + (y0 - ys)**2)
    return u, v

strength_sink = 0
strength_vortex = 5.0
# coordinates of sink
x_sink = 0.0
y_sink = 0.1
# coordinates of vortex
x_vortex = 0.0
y_vortex = 0.0
# coordinates of initial point
x0 = 0.1
y0 = 0.0

dt = 1e-3 # timestep
nt = 150 # number of iterations

# empty arrays for the positions
X = np.zeros(nt)
Y = np.zeros(nt)
# initial positions
X[0], Y[0] = x0, y0

# calculate the path
for i in range(1,nt):
    
    u_v, v_v = get_velocity_vortex(
        strength_vortex,
        x_vortex,
        y_vortex,
        X[i-1],
        Y[i-1]    
    )
    u_s, v_s = get_velocity_sink(
        strength_sink,
        x_sink,
        y_sink,
        X[i-1],
        Y[i-1]
    )

    u = u_v + u_s
    v = v_v + v_s

    X[i],Y[i] = get_next_pos(X[i-1], Y[i-1], u, v, dt)


# plot the path 
plt.scatter(
    x_vortex,
    y_vortex,
    color="red"
)
plt.scatter(
    x_sink,
    y_sink,
    color="green"
)
plt.scatter(
    X,Y,
)
plt.xlim(-0.2,0.2)
plt.ylim(-0.2,0.2)
plt.grid()
plt.tight_layout()
plt.show()
plt.savefig(f"calculate_{strength_vortex}_{strength_sink}.png", dpi=300)
