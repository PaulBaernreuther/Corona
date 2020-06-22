import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
import time

import matplotlib.animation as anim
from rooms import *



class scenario:
    def __init__(self, infection_rate = 0.2, number_infected = 5, deathrate = 0.1, max_infected_time = 20):
        self.number_of_rooms = 20
        self.rooms = []
        self.opt_arangement = 0,0
        self.shape = (50,50)
        self.members = 400
        self.infection_rate = infection_rate
        self.number_infected = number_infected
        self.deathrate = deathrate
        self.max_infected_time = max_infected_time
        self.current_arangement = [0,0]
    def find_opt_arangement(self):
        a, b = fig.get_size_inches()
        return find_opt_arangement(self.number_of_rooms, ratio=(self.shape[1] * a / 2) / (self.shape[0] * b))
    def create_rooms(self):
        i,j = self.find_opt_arangement()
        self.current_arangement = [i,j]
        for l in range(self.number_of_rooms):
            newroom = room(self.number_infected, self.shape)
            newroom.show_on_fig(fig, i, 2 * j, (1 + (l // j)) * j + l + 1)
            newroom.compute_scale(fig)
            the_infected = random.sample(range(self.members), self.number_infected)
            for m in range(self.members):
                if m in the_infected:
                    person = Person(newroom, infected = True)
                else:
                    person = Person(newroom)
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
                #person.position = person.new_random_pos()
                person.wiggle()
                person.register()
            room_scatters = room.draw()
            for scat in room_scatters:
                list_of_scatters.append(scat)
        return list_of_scatters

            #fig.canvas.restore_region(room.axbackground)
            #room.ax.draw_artist(room.scatter)
            #room.ax.draw_artist(room.scatter2)
            #fig.canvas.blit(room.ax.bbox)

    def calculate_infected(self):
        for space in self.rooms:
            for prsn in space.persons:
                if prsn.status == "i":
                    for otherprsn in space.persons:
                        if otherprsn.status == "v":
                            distance = np.linalg.norm(np.array(prsn.position) - np.array(otherprsn.position))
                            if distance <= prsn.radius or distance <= otherprsn.radius:
                                if random.random() <= self.infection_rate:
                                    otherprsn.status = "i"
                                    otherprsn.infected_days = 0

    def calculate_death(self):
        for space in self.rooms:
            for prsn in space.persons:
                if prsn.status == "i":
                    prsn.infected_days += 1
                    if prsn.infected_days >= self.max_infected_time:
                        if random.random() <= self.deathrate:
                            prsn.status = "d"
                        else:
                            prsn.status = "c"



    def time_step(self):
        self.calculate_infected()
        self.calculate_death()




#plt.ion()
fig = plt.figure(figsize=(11,4))
fig.patch.set_facecolor('#123456')
fig.patch.set_alpha(0.7)

k = 9
newscenario = scenario()
newscenario.create_rooms()
newscenario.draw_all_rooms()

start = time.time()
def update(frame_number):
    print("Time ", time.time()-start)
    #newscenario.time_step()
    print(time.time()-start)
    newscenario.update_room_axes()
    return newscenario.update_scatters()


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





