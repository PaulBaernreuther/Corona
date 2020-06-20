import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
import time

import matplotlib.animation as anim
from rooms import *



class scenario:
    def __init__(self):
        self.number_of_rooms = 5
        self.rooms = []
        self.opt_arangement = 0,0
        self.shape = (20,20)
        self.members = 100
    def find_opt_arangement(self):
        a, b = fig.get_size_inches()
        return find_opt_arangement(self.number_of_rooms, ratio=(self.shape[1] * a / 2) / (self.shape[0] * b))
    def create_rooms(self):
        i,j = self.find_opt_arangement()
        for l in range(self.number_of_rooms):
            newroom = room(self.shape)
            newroom.show_on_fig(fig, i, 2 * j, (1 + (l // j)) * j + l + 1)
            newroom.compute_scale(fig)
            for m in range(self.members):
                person = Person(newroom)
                person.register()
            self.rooms.append(newroom)
    def draw_all_rooms(self):
        for thisroom in self.rooms:
            thisroom.draw()
    def update_scatters(self):
        for room in self.rooms:
            room.clear_room()
            room.compute_scale(fig)
            for person in room.persons:
                #person.position = person.new_random_pos()
                person.wiggle()
                person.register()
            room.draw()
            #fig.canvas.restore_region(room.axbackground)
            #room.ax.draw_artist(room.scatter)
            #room.ax.draw_artist(room.scatter2)
            #fig.canvas.blit(room.ax.bbox)




plt.ion()
fig = plt.figure(figsize=(11,4))
fig.patch.set_facecolor('#123456')
fig.patch.set_alpha(0.7)

k = 9
newscenario = scenario()
newscenario.create_rooms()
newscenario.draw_all_rooms()


t = time.time()
counter = 0

fig.canvas.draw()
while(True):
    '''if time.time()-t < 1:
        counter += 1
    else:
        print("fps: ", counter)
        #break'''

    plt.waitforbuttonpress() #auskommentieren falls nicht erwünscht
    #insert some (positions/infections/ etc)- update function here
    newscenario.update_scatters()
    fig.canvas.draw()
    fig.canvas.flush_events()





