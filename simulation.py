import numpy as np
import math
import matplotlib.pyplot as plt

# --- Grid ---
N = 50
x_start, x_end = -2.0, 2.0
y_start, y_end = -1.0, 1.0
x = np.linspace(x_start, x_end, N)
y = np.linspace(y_start, y_end, N)
X, Y = np.meshgrid(x, y)

# --- Vortex parameters ---
# Each vortex is a dict with:
#   strength  : circulation strength (positive = counter-clockwise)
#   x, y      : position of the vortex center
#   aspect_x  : horizontal stretch ratio (>1 = wider oval, <1 = narrower)
#   aspect_y  : vertical stretch ratio   (>1 = taller oval, <1 = shorter)
#   diameter  : core size (larger = bigger vortex, smaller = tighter vortex)
#   viscosity : 0 = inviscid point vortex; higher = more diffuse/smoother core

vortices = [
    # Large circular vortex
    {'strength': 5.0, 'x':  0.0, 'y': -0.3, 'aspect_x': 1.0, 'aspect_y': 1.0, 'diameter': 0.4,  'viscosity': 0.0},
    # Small horizontal oval vortex
    {'strength': 3.0, 'x': -1.0, 'y':  0.3, 'aspect_x': 2.0, 'aspect_y': 0.7, 'diameter': 0.15, 'viscosity': 0.0},
    # Medium vertical oval vortex
    {'strength': 4.0, 'x':  1.2, 'y':  0.2, 'aspect_x': 0.6, 'aspect_y': 1.5, 'diameter': 0.25, 'viscosity': 0.0},
]


def get_velocity_vortex(strength, xv, yv, X, Y, aspect_x=1.0, aspect_y=1.0, diameter=0.3, viscosity=0.0):
    """
    Returns the velocity field of a vortex with oval shape and viscous core.

    aspect_x / aspect_y control the oval shape of the streamlines.
    diameter sets the core size. viscosity diffuses the core further.
    Uses the Lamb-Oseen model to smooth the singularity at the center.
    """
    dx = X - xv
    dy = Y - yv

    # Elliptical squared distance — controls oval vs circular streamlines
    r2 = (dx / aspect_x)**2 + (dy / aspect_y)**2

    # Lamb-Oseen viscous core: diameter sets base size, viscosity expands it
    r_core = diameter * (1.0 + 3.0 * viscosity)
    factor = 1.0 - np.exp(-r2 / r_core**2)

    denom = np.maximum(r2, 1e-10)
    u = +strength / (2 * math.pi) * (dy / aspect_y**2) / denom * factor
    v = -strength / (2 * math.pi) * (dx / aspect_x**2) / denom * factor

    return u, v


def get_stream_function_vortex(strength, xv, yv, X, Y, aspect_x=1.0, aspect_y=1.0):
    dx = X - xv
    dy = Y - yv
    r2 = (dx / aspect_x)**2 + (dy / aspect_y)**2
    psi = strength / (4 * math.pi) * np.log(np.maximum(r2, 1e-10))
    return psi


# --- Superpose all vortices ---
u_total = np.zeros_like(X)
v_total = np.zeros_like(X)
psi_total = np.zeros_like(X)

for vp in vortices:
    u, v_vel = get_velocity_vortex(
        vp['strength'], vp['x'], vp['y'], X, Y,
        vp['aspect_x'], vp['aspect_y'], vp['diameter'], vp['viscosity']
    )
    psi = get_stream_function_vortex(
        vp['strength'], vp['x'], vp['y'], X, Y,
        vp['aspect_x'], vp['aspect_y']
    )
    u_total += u
    v_total += v_vel
    psi_total += psi


# --- Plot ---
width = 10
height = (y_end - y_start) / (x_end - x_start) * width
speed = np.sqrt(u_total**2 + v_total**2)
speed = np.clip(speed, 0, 20)
speed = speed / 20

plt.figure(figsize=(width, height))
plt.xlabel('x', fontsize=16)
plt.ylabel('y', fontsize=16)
plt.xlim(x_start, x_end)
plt.ylim(y_start, y_end)
plt.streamplot(X, Y, u_total, v_total, color=speed, cmap='jet',
               density=2, linewidth=1, arrowsize=1, arrowstyle='->')

# Marker size scales with diameter so bigger vortices show a bigger dot
for vp in vortices:
    plt.scatter(vp['x'], vp['y'], color='#CD2305', s=300 * vp['diameter'], marker='o')

plt.tight_layout()
plt.show()
plt.savefig('simulation.png', dpi=300)
