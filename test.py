import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

fig, ax = plt.subplots()
x = np.arange(0, 2*np.pi, 0.01)
line, = ax.plot(x, np.sin(x))
def animate(i):
    line.set_ydata(np.sin(x + i / 50))  # update the data.
ani = animation.FuncAnimation(
    fig, animate, interval=20)
plt.show()

import numpy as np
from matplotlib import pyplot as plt, animation
plt.rcParams["figure.figsize"] = [7.00, 3.50]
plt.rcParams["figure.autolayout"] = True
fig, ax = plt.subplots()
ax.set(xlim=(-3, 3), ylim=(-1, 1))
x = np.linspace(-3, 3, 91)
t = np.linspace(1, 25, 30)
X2, T2 = np.meshgrid(x, t)
sinT2 = np.sin(2 * np.pi * T2 / T2.max())
F = 0.9 * sinT2 * np.sinc(X2 * (1 + sinT2))
line, = ax.plot(x, F[0, :], color='k', lw=2)
def animate(i):
   line.set_ydata(F[i, :])
anim = animation.FuncAnimation(fig, animate, interval=100, frames=len(t) - 1)
plt.show()