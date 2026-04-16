import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- Grid ---
N = 80
x_start, x_end = -2.0, 2.0
y_start, y_end = -1.0, 1.0
x = np.linspace(x_start, x_end, N)
y = np.linspace(y_start, y_end, N)
X, Y = np.meshgrid(x, y)

# --- Vortex initial conditions ---
# Each vortex moves under the velocity field induced by all others (N-vortex problem).
# strength > 0 = counter-clockwise,  strength < 0 = clockwise
#
# Collision setup: two dipoles on a head-on course.
# A dipole = one + and one - vortex close together — it self-propels.
# Left dipole  (+top, -bottom) → moves RIGHT
# Right dipole (-top, +bottom) → moves LEFT
# They meet in the middle and scatter.
strengths = np.array([ 4.0, -4.0, -4.0,  4.0])
state = {
    'vx': np.array([-1.2, -1.2,  1.2,  1.2]),
    'vy': np.array([ 0.15, -0.15,  0.15, -0.15]),
}

dt = 0.02
trail_len = 80          # number of past frames kept for trajectory trails
history_x = [state['vx'].copy()]
history_y = [state['vy'].copy()]
frame_count = [0]


# --- Physics: N-vortex equations ---

def deriv(vx, vy):
    """
    Velocity of each vortex due to all others — fully vectorised.
    dx[i,j] = vx[i] - vx[j]  (displacement from j to i)
    u[i]    = Σ_j  Γ_j/(2π) * dy[i,j] / r²[i,j]   (j ≠ i)
    """
    dx = vx[:, None] - vx[None, :]
    dy = vy[:, None] - vy[None, :]
    r2 = dx**2 + dy**2
    np.fill_diagonal(r2, np.inf)            # exclude self-interaction
    r2 = np.maximum(r2, 0.001)             # soft-core: prevents blow-up on close approach
    u = np.sum(+strengths[None, :] / (2 * np.pi) * dy / r2, axis=1)
    v = np.sum(-strengths[None, :] / (2 * np.pi) * dx / r2, axis=1)
    return u, v


def rk4_step(vx, vy):
    """4th-order Runge-Kutta integration of vortex positions."""
    k1u, k1v = deriv(vx,                   vy)
    k2u, k2v = deriv(vx + 0.5*dt*k1u,     vy + 0.5*dt*k1v)
    k3u, k3v = deriv(vx + 0.5*dt*k2u,     vy + 0.5*dt*k2v)
    k4u, k4v = deriv(vx +     dt*k3u,     vy +     dt*k3v)
    new_vx = vx + dt / 6 * (k1u + 2*k2u + 2*k3u + k4u)
    new_vy = vy + dt / 6 * (k1v + 2*k2v + 2*k3v + k4v)
    return new_vx, new_vy


def flow_field(vx, vy):
    """Total velocity on the mesh grid from all vortices at their current positions."""
    u = np.zeros((N, N))
    v = np.zeros((N, N))
    for g, xi, yi in zip(strengths, vx, vy):
        dx = X - xi;  dy = Y - yi
        r2 = np.maximum(dx**2 + dy**2, 1e-10)
        u += +g / (2 * np.pi) * dy / r2
        v += -g / (2 * np.pi) * dx / r2
    return u, v


def particle_velocity(vx_v, vy_v, px, py):
    """Velocity at particle positions (for advecting tracers)."""
    u = np.zeros(len(px))
    v = np.zeros(len(py))
    for g, xi, yi in zip(strengths, vx_v, vy_v):
        dx = px - xi;  dy = py - yi
        r2 = np.maximum(dx**2 + dy**2, 1e-10)
        u += +g / (2 * np.pi) * dy / r2
        v += -g / (2 * np.pi) * dx / r2
    return u, v


# --- Particles (Ventusky-style tracers) ---
n_par = 800
px = np.random.uniform(x_start, x_end, n_par)
py = np.random.uniform(y_start, y_end, n_par)

# --- Figure ---
fig, ax = plt.subplots(figsize=(10, 5))
ax.set_facecolor('black')
fig.patch.set_facecolor('#060610')

u0, v0 = flow_field(state['vx'], state['vy'])
speed0 = np.clip(np.sqrt(u0**2 + v0**2), 0, 12)
mesh = ax.pcolormesh(X, Y, speed0, cmap='inferno', shading='auto', vmin=0, vmax=12)

cbar = fig.colorbar(mesh, ax=ax, pad=0.02)
cbar.set_label('Speed', color='white', fontsize=11)
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')

scat = ax.scatter(px, py, s=1.5, c='white', alpha=0.5, linewidths=0)

# Vortex markers: red = counter-clockwise, blue = clockwise
colors_v = ['#ff5555' if g > 0 else '#5599ff' for g in strengths]
vortex_scat = ax.scatter(state['vx'], state['vy'], s=80, c=colors_v,
                          zorder=5, edgecolors='white', linewidths=0.8)

# Trajectory trails — one coloured line per vortex
trail_lines = [
    ax.plot([], [], '-', color=c, alpha=0.5, linewidth=1.2)[0]
    for c in colors_v
]

ax.set_xlim(x_start, x_end)
ax.set_ylim(y_start, y_end)
ax.set_xlabel('x', color='white', fontsize=13)
ax.set_ylabel('y', color='white', fontsize=13)
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_edgecolor('#333333')

# Container for streamplot — must be removed and redrawn each frame
sp = [None]


def update(frame):
    # Step vortex positions forward with RK4
    state['vx'], state['vy'] = rk4_step(state['vx'], state['vy'])
    history_x.append(state['vx'].copy())
    history_y.append(state['vy'].copy())
    if len(history_x) > trail_len:
        history_x.pop(0)
        history_y.pop(0)

    # Update background speed field
    u_g, v_g = flow_field(state['vx'], state['vy'])
    speed = np.clip(np.sqrt(u_g**2 + v_g**2), 0, 12)
    mesh.set_array(speed.ravel())

    # Remove old streamplot and draw new one showing current flow direction
    if sp[0] is not None:
        sp[0].lines.remove()
        sp[0].arrows.remove()
    sp[0] = ax.streamplot(X, Y, u_g, v_g, color='white', density=1.5,
                          linewidth=0.7, arrowsize=1.0, arrowstyle='->',
                          alpha=0.5, zorder=3)

    # Advect particles through the current field
    u_p, v_p = particle_velocity(state['vx'], state['vy'], px, py)
    px[:] += u_p * dt
    py[:] += v_p * dt
    out = (px < x_start) | (px > x_end) | (py < y_start) | (py > y_end)
    px[out] = np.random.uniform(x_start, x_end, out.sum())
    py[out] = np.random.uniform(y_start, y_end, out.sum())
    scat.set_offsets(np.c_[px, py])

    # Move vortex markers
    vortex_scat.set_offsets(np.c_[state['vx'], state['vy']])

    # Draw trajectory trails
    hx = np.array(history_x)   # shape (trail_len, n_vortices)
    hy = np.array(history_y)
    for i, line in enumerate(trail_lines):
        line.set_data(hx[:, i], hy[:, i])

    frame_count[0] += 1
    ax.set_title(
        f'N-Vortex Interaction  |  t = {frame_count[0] * dt:.2f}  '
        f'|  red = CCW  blue = CW',
        color='white', fontsize=11, pad=6
    )


ani = animation.FuncAnimation(fig, update, frames=500, interval=40, blit=False)
plt.tight_layout()
plt.show()
