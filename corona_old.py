import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
import time

from old_classes import *

fig = plt.figure(figsize=(11,6))

test_room = room()
a,b = fig.get_size_inches()
test_room.size_on_screen = (a/2, b)
test_room.init_ax(fig)

for i in range(1000):
    person = Person(test_room)
    person.register()

test_room.draw()

def new_room(members, act, loc, size):
    new_room = room()
    new_room.actual_size = act
    new_room.location_on_screen = loc
    new_room.size_on_screen = size
    new_room.init_ax(fig)
    for i in range(members):
        person = Person(new_room)
        person.register()
    new_room.draw()
    return new_room

new_room(1000, (10,7), (0.2,0.5), (1,1))
new_room(300, (4,7), (0.4,0.5), (3,1))
new_room(100, (1,1), (0.1,0.1), (3,3))
new_room(600, (4,3), (0.4,0.1), (6,7))
new_room(300, (10,7), (0.2,0.5), (1,1))
new_room(200, (3,2), (0.3,0), (3,3))
new_room(600, (2,1), (0.4,0.3), (3,2))
new_room(1000, (3,7), (0.8,0.1), (2,2))


plt.show()


