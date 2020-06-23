from mpl_toolkits.axes_grid1 import Divider, Size
import numpy as np
import random
from functions import *

from matplotlib.colors import ListedColormap, BoundaryNorm

radius_to_sice = 144
radius = 0.5
aura_on = True
colors = {"i":'r',"v":'b',"c": 'g',"d": 'k'}
cmap = ListedColormap(colors.values())
norm = BoundaryNorm([0,1,2,3,4], cmap.N)


class Room:
    def __init__(self, number_infected, act_size = (3,4), members = 100):
        #plot-stuff
        self.border = 2
        self.ax = None
        self.axbackground = None
        self.divider = None
        self.location_on_screen = (0.5,0)
        self.size_on_screen = (1,1)
        self.actual_size = act_size
        if self.actual_size[0]<2*self.border or self.actual_size[1]<2*self.border:
            raise ValueError("Everything is border")
        self.boxpos = (0,0)
        self.scale = 1
        self.draw_data = [[],[],[]]
        self.draw_data2 = [[],[],[]]
        self.scatter = None
        self.scatter2 = None

        self.members = members
        self.number_infected = number_infected

        self.persons = []
        self.data = {"i": [], "v": [], "c": [], "d": []}

    def update_data(self):
        for char in ["i", "v", "c", "d"]:
            self.data[char].append(0)
        for person in self.persons:
            self.data[person.status][-1] += 1

    def calculate_infected(self, list_of_infected):
        discrete_raster = [[[] for i in range(self.actual_size[1])] for j in range(self.actual_size[0])]
        for person in self.persons:
            x, y = int(person.position[0]), int(person.position[1])
            discrete_raster[x][y].append(person)
        pers_sorted_by_radius = sorted([person for person in self.persons if person.status in ["v", "i"]], key=lambda person: -person.radius)
        for count, person in enumerate(pers_sorted_by_radius):
            person.index = count
        for person in pers_sorted_by_radius:
            x, y = int(person.position[0]), int(person.position[1])
            rad = person.radius
            rad_int = int(rad)
            i_min = max(x-rad_int, 0)
            i_max = min(x+rad_int+1, int(self.actual_size[0])-1)
            j_min = max(y-rad_int, 0)
            j_max = min(y+rad_int+1, int(self.actual_size[1])-1)
            index = person.index
            current_radius = person.radius
            curr_status = person.status
            get_infected = False
            for i in range(i_min, i_max):
                for j in range(j_min, j_max):
                    for otherperson in discrete_raster[i][j]:
                        if otherperson.index >= index:
                            continue
                        distance = np.linalg.norm(np.array(person.position) - np.array(otherperson.position))
                        if distance <= current_radius:
                            if random.random() <= person.infectionrate:
                                if curr_status == "i":
                                    otherperson.status = "i"
                                elif otherperson.status == "i":
                                    get_infected = True
            if get_infected:
                person.status = "i"
                person.infected_days = 0
                list_of_infected.append(person)



    def calculate_death(self, beds):
        for prsn in self.persons:
            if prsn.status == "i":
                prsn.infected_days += 1
                if prsn.infected_days >= prsn.max_infected_time:
                    if prsn.is_in_bed:
                        beds += 1
                        if random.random() <= prsn.deathrate:
                            prsn.status = "d"
                        else:
                            prsn.status = "c"
                    else:
                        if random.random() <= prsn.deathrate_without_healthcare:
                            prsn.status = "d"
                        else:
                            prsn.status = "c"
        return beds

    def compute_scale(self, fig):
        a,b = get_ax_size(self.ax, fig)
        if self.actual_size[0]/self.actual_size[1] > a/b:
            self.size_on_screen = [a, (a/self.actual_size[0])*self.actual_size[1]]
            self.scale = (a/self.actual_size[0])
            self.boxpos = (0, (b-((a/self.actual_size[0])*self.actual_size[1]))/2)
        else:
            self.size_on_screen = [(b/self.actual_size[1])*self.actual_size[0], b]
            self.scale = (b/self.actual_size[1])
            self.boxpos = ((a-((b/self.actual_size[1])*self.actual_size[0]))/2, 0)

    def show_on_fig(self, fig, rows, cols, index):
        self.ax = fig.add_subplot(rows, cols, index, adjustable = "box", aspect = 1)
        self.axbackground = fig.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        self.ax.set_xlim(0, self.actual_size[0])
        self.ax.set_ylim(0, self.actual_size[1])
        self.scatter = None
        self.scatter2 = None

    def clear_room(self):
        self.draw_data = [[], [], []]
        self.draw_data2 = [[], [], []]
    def draw(self):
        if not self.scatter:
            self.scatter = self.ax.scatter(self.draw_data[0], self.draw_data[1], c = self.draw_data[2], s = (radius*radius_to_sice)**2*self.scale**2, cmap = cmap, norm = norm)
            if aura_on:
                self.scatter2 = self.ax.scatter(self.draw_data2[0], self.draw_data2[1], sizes = self.draw_data2[2], c = "r", alpha= 0.1)
        else:
            self.scatter.set_offsets(np.c_[self.draw_data[0], self.draw_data[1]])
            self.scatter.set_array(np.array(self.draw_data[2]))
            self.scatter.set_sizes(np.array([(radius*radius_to_sice)**2*self.scale**2 for item in range(len(self.draw_data[0]))]))
            if aura_on:
                self.scatter2.set_offsets(np.c_[self.draw_data2[0], self.draw_data2[1]])
                self.scatter2.set_sizes(np.array(self.draw_data2[2]))
        if aura_on:
            return [self.scatter, self.scatter2]
        return [self.scatter]



class Person:
    def __init__(self, room, infectionrate = 0.2, deathrate = 0.01, deathrate_without_healthcare = 0.05, max_infected_time = 10, speed = 0.5, radius = 2):

        self.room = room
        self.status = "v"
        self.infected_days = 0
        self.position = self.new_random_pos()

        self.max_infected_time = max_infected_time
        self.deathrate = deathrate
        self.deathrate_without_healthcare = deathrate_without_healthcare
        self.infectionrate = infectionrate
        self.speed = speed
        self.radius = radius


        self.radius_anim_percentage = 1
        self.room.persons.append(self)
        self.angle = random.random()
        self.direction = [0,0]#uniform distr is wahrscheinlich nicht gut
        self.is_in_bed = False

    def new_random_pos(self):
        return [self.room.border+np.random.random()*(self.room.actual_size[0]-2*self.room.border), self.room.border+np.random.random()*(self.room.actual_size[1]-2*self.room.border)]
    def keep_going(self):
        if not (self.room.border<self.position[0]<self.room.actual_size[0]-self.room.border and self.room.border<self.position[1]<self.room.actual_size[1]-self.room.border):
            angle_diff = 0.5
        else:
            angle_diff = np.random.normal(0, 0.1, 1)
            if math.fabs(angle_diff)>0.5:
                angle_diff = 0
        self.angle = (self.angle + angle_diff) % 1
        self.direction[0] = self.speed * math.cos(self.angle*2*math.pi)
        self.direction[1] = self.speed * math.sin(self.angle*2*math.pi)
        self.position = [self.position[0]+self.direction[0], self.position[1]+self.direction[1]]
    def wiggle(self):
        factor = 1
        old_position = self.position
        while True:
            self.position[0] += np.random.random()*(factor)
            self.position[1] += np.random.random()*(factor)
            self.position[0] -= np.random.random()*(factor)
            self.position[1] -= np.random.random()*(factor)
            if (self.room.actual_size[0]>self.position[0]>0 and self.room.actual_size[1]>self.position[1]>0) or True:
                break
            print("we got to far")
            self.position = old_position
    def register(self):
        colors = { "i": 0.5, "v": 1.5, "c": 2.5, "d": 3.5}
        color = colors[self.status]
        self.room.draw_data[0].append(self.position[0])
        self.room.draw_data[1].append(self.position[1])
        self.room.draw_data[2].append(color)
        if self.status == "i":
            self.room.draw_data2[0].append(self.position[0])
            self.room.draw_data2[1].append(self.position[1])
            self.room.draw_data2[2].append(((self.radius*self.radius_anim_percentage)**2)*(self.room.scale**2)*radius_to_sice**2)





