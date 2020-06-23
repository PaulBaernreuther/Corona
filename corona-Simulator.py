import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
import time

import matplotlib.animation as anim
from rooms import *

class scenario:
    def __init__(self, number_infected = 5, deathrate = 0.1, max_infected_time = 20, infectionrate = 0.2, shape = (100,100), members = 2000, radius = 2):
        self.number_of_rooms = 1
        self.shape = shape
        self.members = members
        self.number_infected = number_infected
        self.deathrate = deathrate
        self.max_infected_time = max_infected_time
        self.infectionrate = infectionrate
        self.radius = radius

        self.rooms = []
        self.opt_arangement = 0,0
        self.current_arangement = [0,0]
        self.data = {"i": [], "v": [], "c": [], "d": []}
    def find_opt_arangement(self):
        a, b = fig.get_size_inches()
        return find_opt_arangement(self.number_of_rooms, ratio=(self.shape[1] * a / 2) / (self.shape[0] * b))
    def create_rooms(self):
        i,j = self.find_opt_arangement()
        self.current_arangement = [i,j]
        for l in range(self.number_of_rooms):
            newroom = Room(number_infected=self.number_infected, act_size = self.shape, members = self.members)
            newroom.show_on_fig(fig, i, 2 * j, (1 + (l // j)) * j + l + 1)
            newroom.compute_scale(fig)
            the_infected = random.sample(range(self.members), self.number_infected)
            for m in range(self.members):
                person = Person(newroom, max_infected_time=self.max_infected_time, deathrate=self.deathrate, infectionrate= self.infectionrate, radius = self.radius)
                if m in the_infected:
                    person.status = "i"
                person.register()
            self.rooms.append(newroom)
    def update_room_axes(self):
        i,j = self.find_opt_arangement()
        if i != self.current_arangement[0] or j != self.current_arangement[1]:
            for l, room in enumerate(self.rooms):
                room.ax.remove()
                room.show_on_fig(fig, i, 2 * j, (1 + (l // j)) * j + l + 1)
            self.current_arangement = [i, j]
    def draw_all_rooms(self):
        for thisroom in self.rooms:
            thisroom.draw()
    def update_scatters(self):
        list_of_scatters = []
        for room in self.rooms:
            room.clear_room()
            room.compute_scale(fig)
            for person in room.persons:
                person.keep_going()
                #person.position = person.new_random_pos()
                #person.wiggle()
                person.register()
            room_scatters = room.draw()
            for scat in room_scatters:
                list_of_scatters.append(scat)
        return list_of_scatters

    def update_data(self):
        for char in ["i", "v", "c", "d"]:
            self.data[char].append(0)
        for room in self.rooms:
            room.update_data()
            for char in ["i", "v", "c", "d"]:
                self.data[char][-1] += room.data[char][-1]

    def update_graph(self):
        out = {}
        for char in ["i", "v", "c", "d"]:
            out[char] = np.array([0]+self.data[char]+[0])
        return np.array([0]+[i for i in range(len(self.data["i"]))]+[len(self.data["i"])-1]), out

    def update_relative_graph(self):
        out = {}
        size = (len(self.data["i"]))
        for charlist in ["i", ["v","i"], ["c","v", "i"], ["d","c", "v", "i"]]:
            out[charlist[0]] = np.array([0] + [sum([self.data[char][item] for char in charlist]) for item in range(size)] + [0])
        return np.array([0] + [i for i in range(size)] + [len(self.data["i"]) - 1]), out

    def calculate_infected(self):
        for room in self.rooms:
            room.calculate_infected()

    def calculate_death(self):
        for room in self.rooms:
            room.calculate_death()

    def time_step(self):
        self.calculate_infected()
        self.calculate_death()
        self.update_data()




#plt.ion()
fig = plt.figure(figsize=(11,4))
fig.patch.set_facecolor('#123456')
fig.patch.set_alpha(0.7)
ax = fig.add_subplot(2,2,1)



k = 9
newscenario = scenario()
newscenario.create_rooms()
newscenario.draw_all_rooms()

start = time.time()
def update(frame_number):
    newscenario.time_step()
    newscenario.update_room_axes()
    x, data = newscenario.update_relative_graph()
    ax.clear()
    for char in ["d", "c", "v", "i"]:
        ax.fill(x, data[char], c = colors[char])
    return newscenario.update_scatters()+[ax]


animation = FuncAnimation(fig, update, interval=1, blit = True)

plt.show()


'''t = time.time()
counter = 0


fig.canvas.draw()
while(True):
    if time.time()-t < 1:
        counter += 1
    else:
        print("fps: ", counter)
        #break

    #plt.waitforbuttonpress() #auskommentieren falls nicht erwünscht
    #insert some (positions/infections/ etc)- update function here
    newscenario.time_step()
    newscenario.update_room_axes()
    newscenario.update_scatters()
    fig.canvas.draw()
    fig.canvas.flush_events()'''





