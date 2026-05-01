import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.cm as cm
import matplotlib.colors as mcolors

# --- Grid ---
N = 80
x_start, x_end = -2.0, 2.0
y_start, y_end = -1.0, 1.0
x = np.linspace(x_start, x_end, N)
y = np.linspace(y_start, y_end, N)
X, Y = np.meshgrid(x, y)

# --- Physics ---
# Kinematic viscosity. Water = 1e-6 m²/s in SI.
# Scaled here so the decay is visible over the animation duration.
nu = 0.005

# Fixed vortex positions — cores grow over time via Lamb-Oseen:
#   r_c(t) = sqrt(4 * nu * t + r0²)
vortices = [
    {'strength':  -5.0, 'x':  -1.5, 'y':  -0.9, 'r0': 0.05},
    {'strength': -4.0, 'x': -0.5, 'y':  -0.5, 'r0': 0.05},
    {'strength':  5.0, 'x':  1.0, 'y': 0.5, 'r0': 0.1},
    {'strength': -1.0, 'x': 1.0, 'y': -0.8, 'r0': 0.01}
]

dt = 0.1
t = [0.5]


def velocity_field(t_val, px=None, py=None):
    u_g = np.zeros((N, N))
    v_g = np.zeros((N, N))
    u_p = np.zeros(len(px)) if px is not None else None
    v_p = np.zeros(len(py)) if py is not None else None

    for vp in vortices:
        r_c = np.sqrt(4.0 * nu * t_val + vp['r0']**2)
        g   = vp['strength']
        dx = X - vp['x'];  dy = Y - vp['y']
        r2 = np.maximum(dx**2 + dy**2, 1e-10)
        fac = 1.0 - np.exp(-r2 / r_c**2)
        u_g += +g / (2 * np.pi) * dy / r2 * fac
        v_g += -g / (2 * np.pi) * dx / r2 * fac

        if px is not None:
            dpx = px - vp['x'];  dpy = py - vp['y']
            r2p = np.maximum(dpx**2 + dpy**2, 1e-10)
            facp = 1.0 - np.exp(-r2p / r_c**2)
            u_p += +g / (2 * np.pi) * dpy / r2p * facp
            v_p += -g / (2 * np.pi) * dpx / r2p * facp

    return u_g, v_g, u_p, v_p


# --- Particles ---
n_par = 600
px = np.random.uniform(x_start, x_end, n_par)
py = np.random.uniform(y_start, y_end, n_par)

# --- Figure ---
fig, ax = plt.subplots(figsize=(10, 5))

# Fixed colorbar for jet-colored streamlines (speed normalized 0-1)
sm = cm.ScalarMappable(cmap='jet', norm=mcolors.Normalize(vmin=0, vmax=1))
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, pad=0.02)
cbar.set_label('Speed (normalised)', fontsize=11)

u0, v0, _, _ = velocity_field(t[0])
plt.tight_layout()


def draw_frame(u_g, v_g):
    ax.cla()
    ax.set_facecolor('white')

    # Streamlines coloured by speed — same style as vortex.py
    speed = np.sqrt(u_g**2 + v_g**2)
    speed = np.clip(speed, 0, 20)
    speed = speed / 20
    ax.streamplot(X, Y, u_g, v_g, color=speed, cmap='jet',
                  density=2, linewidth=1, arrowsize=1, arrowstyle='->')

    # Particles (dark so visible on white)
    ax.scatter(px, py, s=1.5, c='#444444', alpha=0.4, linewidths=0, zorder=2)

    # Vortex markers + growing core circles
    for vp in vortices:
        color = '#CC2222' if vp['strength'] > 0 else '#2255CC'
        ax.scatter(vp['x'], vp['y'], s=60, color=color, zorder=5,
                   edgecolors='black', linewidths=0.6)
        r_c = np.sqrt(4.0 * nu * t[0] + vp['r0']**2)
        circle = plt.Circle((vp['x'], vp['y']), radius=r_c,
                             fill=False, color='gray', linewidth=0.8,
                             alpha=0.7, linestyle='--')
        ax.add_patch(circle)

    ax.set_xlim(x_start, x_end)
    ax.set_ylim(y_start, y_end)
    ax.set_xlabel('x', fontsize=13)
    ax.set_ylabel('y', fontsize=13)
    ax.set_title(f'Lamb-Oseen Viscous Decay  |  t = {t[0]:.1f}  |  ν = {nu}', fontsize=11)


def update(frame):
    u_g, v_g, u_p, v_p = velocity_field(t[0], px, py)

    px[:] += u_p * dt
    py[:] += v_p * dt
    out = (px < x_start) | (px > x_end) | (py < y_start) | (py > y_end)
    px[out] = np.random.uniform(x_start, x_end, out.sum())
    py[out] = np.random.uniform(y_start, y_end, out.sum())

    draw_frame(u_g, v_g)
    t[0] += dt


ani = animation.FuncAnimation(fig, update, frames=120, interval=60, blit=False)

# Save initial frame as PNG
draw_frame(u0, v0)
plt.savefig('lamb_oseen.png', dpi=150, bbox_inches='tight')
print("Saved lamb_oseen.png")

print("Saving lamb_oseen.gif ...")
ani.save('lamb_oseen.gif', writer='pillow', fps=20)
print("Done — open lamb_oseen.gif in the VS Code file explorer.")
