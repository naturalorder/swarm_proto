import os
os.chdir('C:/Users/jm/Documents/GitHub/swarm_proto')

import random
import sys
import numpy as np
import math
import scipy
import matplotlib.pyplot as plt
from numpy.linalg import norm
from scipy.spatial.distance import cdist, pdist, euclidean

import simulation.bsim as bsim
import behtree.treegen as tg
import behtree.tree_nodes as tree_nodes
import evo.evaluate as evaluate
import evo.operators as op

from matplotlib import animation
# rc, rcParams
# rcParams['animation.embed_limit'] = 2**128
from IPython.display import HTML



# First set up the figure, the axis, and the plot element we want to animate
fig, (ax1, ax2) = plt.subplots(nrows=1,ncols=2, figsize=(16,8), dpi=70, facecolor='w', edgecolor='k')
plt.close()

dim = 2550
ax1.set_xlim((-dim, dim))
ax1.set_ylim((-dim, dim))

fontsize = 12
ax2.set_xlabel('Time (seconds)', fontsize = fontsize)
ax2.set_ylabel('Percentage of Targets Found -(%)', fontsize = fontsize)

# Set how data is plotted within animation loop
global line, line1
line, = ax1.plot([], [], 'gh', markersize = 6, markeredgecolor="black", alpha = 0.9)
line1, = ax1.plot([], [], 'bd', markersize = 8, markeredgecolor="black", alpha = 0.5)
box_line, = ax2.plot([],[], 'r-', markersize = 5)

fsize = 12
time_text = ax1.text(-2000, 2600, '', fontsize = fsize)
box_text = ax1.text(0, 2600, '', color = 'red', fontsize = fsize)
line.set_data([], [])
line1.set_data([], [])

def init():
    line.set_data([], [])
    line1.set_data([], [])
    box_line.set_data([], [])
    return (line, line1, box_line,)


# Create the swarm
swarmsize = 25 # Here you can change the size of the swarm.
swarm = bsim.swarm()
swarm.size = swarmsize
swarm.speed = 3
swarm.gen_agents()

# Create the environment
env = bsim.map()
env.env1()
env.gen()
swarm.map = env

# Create the set of boxes to collect
boxes = bsim.boxes()
boxes.number_of_boxes = 20
bsim.poaching.hover = False
boxes.set_state('random')
boxes.sequence = False
boxes.radius = 100

# Plot collection reg

# plot the walls
[ax1.plot([swarm.map.obsticles[a].start[0], swarm.map.obsticles[a].end[0]], 
    [swarm.map.obsticles[a].start[1], swarm.map.obsticles[a].end[1]], 'k-', lw=2) for a in range(len(swarm.map.obsticles))]

# Set simulation duration
timesteps = 7200

ax2.set_xlim((0, timesteps))
ax2.set_ylim((0, 100))
ax2.set_yticks(np.arange(0, 100, 10))
ax2.grid()

# Add agent motion noise
noise = np.random.uniform(-.1,.1,(timesteps, swarm.size, 4))
score = 0

# Here you can change the swarms behvaior
swarm.behaviour = 'rot_anti'
# This value adjusts the rate the agents change their headings
swarm.param = 0.0085


field, grid = bsim.potentialField_map(swarm.map)
swarm.field = field
swarm.grid = grid

box_data = []
time_data = []
heat_data = []

def animate(i):

    swarm.iterate(noise[i-1])
    swarm.get_state()
    score = boxes.get_state(swarm, i)

    box_data.append(100*(score/len(boxes.boxes)))
    time_data.append(i)

    time_text.set_text('Time: (%d/%d)' % (i, timesteps))
    box_text.set_text('Poachers Found: (%d/%d)' % (score,len(boxes.boxes)))
    
    line1.set_data(boxes.boxes.T[0], boxes.boxes.T[1])
    line.set_data(swarm.agents.T[0], swarm.agents.T[1])
    box_line.set_data(time_data, box_data)

    return (line, line1, box_line, time_text, box_text)

anim = animation.FuncAnimation(fig, animate, init_func=init,
                            frames=timesteps, interval=100, blit=True, cache_frame_data = False)

# Note: below is the part which makes it work on Colab
# rc('animation', html='jshtml')
# plt.rcParams['animation.ffmpeg_path'] = 'C:/ffmpeg-5.0.1-full_build/bin'




anim.save('sim_animation.mp4', writer='ffmpeg', fps=100, dpi=200)