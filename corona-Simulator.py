import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
import time

import matplotlib.animation as anim
from rooms import *

class scenario:
    def __init__(self, number_infected = 3, deathrate = 0.01, deathrate_without_healthcare = 0.05, max_infected_time = 20, infectionrate = 0.2, shape = (100,100), members = 2000, radius = 2, healthcare_max = 0.02, bed_chance = 0.05):
        self.number_of_rooms = 1
        self.shape = shape
        self.members = members
        self.number_infected = number_infected
        self.deathrate = deathrate
        self.deathrate_without_healthcare = deathrate_without_healthcare
        self.max_infected_time = max_infected_time
        self.infectionrate = infectionrate
        self.radius = radius
        self.healthcare_max = int(members * healthcare_max)
        self.bed_chance = bed_chance

        self.rooms = []
        self.opt_arangement = 0,0
        self.current_arangement = [0,0]
        self.data = {"i": [], "v": [], "c": [], "d": []}
        self.list_of_infected = []
        self.beds = self.healthcare_max
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
                person = Person(newroom, max_infected_time=self.max_infected_time, deathrate=self.deathrate, deathrate_without_healthcare=self.deathrate_without_healthcare, infectionrate= self.infectionrate, radius = self.radius)
                if m in the_infected:
                    person.status = "i"
                person.register()
            self.rooms.append(newroom)
    def new_room(self, size = None):
        if size:
            shape = size
        else:
            shape = self.shape
        specialroom = Room(number_infected=self.number_infected, act_size = shape, members = self.members)
        self.number_of_rooms += 1
        i, j = self.find_opt_arangement()
        for l, room in enumerate(self.rooms):
            room.ax.remove()
            room.show_on_fig(fig, i, 2 * j, (1 + (l // j)) * j + l + 1)
        l = self.number_of_rooms - 1
        specialroom.show_on_fig(fig, i, 2 * j, (1 + (l // j)) * j + l + 1)
        self.current_arangement = [i, j]
        self.rooms.append(specialroom)
        return specialroom
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
            room.calculate_infected(self.list_of_infected)

    def calculate_beds(self):
        for prsn in self.list_of_infected.copy():
            if random.random() <= self.bed_chance and self.beds > 0:
                self.beds -= 1
                prsn.is_in_bed = True
            self.list_of_infected.remove(prsn)


    def calculate_death(self):
        for room in self.rooms:
            self.beds = room.calculate_death(self.beds)

    def time_step(self):
        self.calculate_infected()
        self.calculate_death()
        self.update_data()

    def jump(self, prsn, codomain, pos = None):
        prsn.room.persons.remove(prsn)
        codomain.persons.append(prsn)
        prsn.room = codomain
        if not pos:
            prsn.position = prsn.new_random_pos()
        else:
            prsn.position = pos
        prsn.room.members -= 1
        codomain.members += 1



class ClusterScenario(scenario):
    def __init__(self, jumpy_percentage = 0.01, jumptime = 10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jumpy_percentage = jumpy_percentage
        self.jumptime = jumptime
        self.time_since_jump = 0

    def create_rooms(self):
        super().create_rooms()
        for room in self.rooms:
            for prsn in room.persons:
                prsn.jumpy = False
                prsn.time_since_jump = int(random.random()*self.jumptime)
        for room in self.rooms:
            quantity = len(room.persons)
            the_jumpies = random.sample(range(quantity), int(quantity*self.jumpy_percentage))
            for number in the_jumpies:
                room.persons[number].jumpy = True

    def update_scatters(self):
        list_of_jumpers =[]
        for room in self.rooms:
            for prsn in room.persons:
                if prsn.jumpy:
                    prsn.time_since_jump += 1
                    if prsn.time_since_jump >= self.jumptime:
                        prsn.time_since_jump = 0
                        list_of_jumpers.append(prsn)
        for jumper in list_of_jumpers:
            self.jump(jumper, random.choice(self.rooms))
        return super().update_scatters()


class Supermarket(scenario):
    def __init__(self, shopping_time = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.shopping_time = shopping_time

    def create_rooms(self):
        super().create_rooms()
        for room in self.rooms:
            for prsn in room.persons:
                prsn.purchase_interval = 50 + int(random.random() * 20 - 2)
                prsn.time_since_purchase = int(random.random()*prsn.purchase_interval)
                prsn.time_in_market = 0
                prsn.room_of_origin = prsn.room
                prsn.home = prsn.position
        self.market = self.new_room(size = [10,30])
        self.market.ax.set_title("Supermercado")

    def update_scatters(self):
        list_of_thrifters = []
        for room in self.rooms:
            for prsn in room.persons:
                if prsn.room is self.market:
                    prsn.time_in_market += 1
                    if prsn.time_in_market >= self.shopping_time:
                        prsn.time_in_market = 0
                        prsn.purchase_interval = 50 + int(random.random() * 20 - 2)
                        self.jump(prsn, prsn.room_of_origin, prsn.home)
                    continue
                prsn.time_since_purchase += 1
                if prsn.time_since_purchase >= prsn.purchase_interval:
                    prsn.time_since_purchase = 0
                    list_of_thrifters.append(prsn)
        for prsn in list_of_thrifters:
            prsn.home = prsn.position
            self.jump(prsn, self.market)
        return super().update_scatters()


fig = plt.figure(figsize=(11,4))
fig.patch.set_facecolor('#123456')
fig.patch.set_alpha(0.7)
ax = fig.add_subplot(2,2,1)



k = 9
newscenario = Supermarket()
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





