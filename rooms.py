from mpl_toolkits.axes_grid1 import Divider, Size
import numpy as np
import random
from functions import *

radius_to_sice = 144
radius = 0.5


class room:
    def __init__(self, act_size = (3,4)):
        self.ax = None
        self.axbackground = None
        self.divider = None
        self.location_on_screen = (0.5,0)
        self.size_on_screen = (1,1)
        self.actual_size = act_size
        self.boxpos = (0,0)
        self.members = 0
        self.scale = 1
        self.border = 0.1
        self.draw_data = [[],[],[]]
        self.draw_data2 = [[],[],[]]
        self.scatter = None
        self.scatter2 = None
        self.persons = []
    '''def get_divider(self, fig):
        self.border = 0.1
        while self.actual_size[0] < (self.size_on_screen[0]-2*self.border) and self.actual_size[1]<(self.size_on_screen[1]-2*self.border):
            self.border += 0.1
        x_factor= self.actual_size[0]/(self.size_on_screen[0]-2*self.border)
        y_factor = self.actual_size[1]/(self.size_on_screen[1]-2*self.border)
        self.scale = max(x_factor, y_factor)
        draw_size = (self.actual_size[0]/self.scale, self.actual_size[1]/self.scale)
        h = [Size.Fixed(self.border), Size.Fixed(draw_size[0])]
        v = [Size.Fixed(self.border), Size.Fixed(draw_size[1])]
        return Divider(fig, (self.location_on_screen[0], self.location_on_screen[1], 1, 1), h, v, aspect=False)
    def init_ax(self ,fig):
        h = [Size.Fixed(self.size_on_screen[0])]
        v = [Size.Fixed(self.size_on_screen[1])]
        self.divider = self.get_divider(fig)
        self.ax = fig.add_axes(self.divider.get_position(),axes_locator=self.divider.new_locator(nx=1, ny=1))
        #self.ax.get_xaxis().set_visible(False)
        #self.ax.get_yaxis().set_visible(False)
        self.ax.set_xlim(0, self.actual_size[0])
        self.ax.set_ylim(0, self.actual_size[1])'''
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
        #self.ax.get_xaxis().set_visible(False)
        #self.ax.get_yaxis().set_visible(False)
        self.ax.set_xlim(0, self.actual_size[0])
        self.ax.set_ylim(0, self.actual_size[1])

    def clear_room(self):
        self.draw_data = [[], [], []]
        self.draw_data2 = [[], [], []]
    def draw(self):
        if not self.scatter:
            self.scatter = self.ax.scatter(self.draw_data[0], self.draw_data[1], c = self.draw_data[2], s = (radius*radius_to_sice)**2*self.scale**2)
            self.scatter2 = self.ax.scatter(self.draw_data2[0], self.draw_data2[1], sizes = self.draw_data2[2], c = "r", alpha= 0.1)
        else:
            self.scatter.set_offsets(np.c_[self.draw_data[0], self.draw_data[1]])
            self.scatter.set_array(np.array(self.draw_data[2]))
            self.scatter.set_sizes(np.array([(radius*radius_to_sice)**2*self.scale**2 for item in range(len(self.draw_data[0]))]))
            self.scatter2.set_offsets(np.c_[self.draw_data2[0], self.draw_data2[1]])
            self.scatter2.set_sizes(np.array(self.draw_data2[2]))



class Person:
    def __init__(self, room):
        self.status = random.choice(["v", "i", "c", "d"])
        self.room = room
        self.position = self.new_random_pos()
        self.radius = 2

        self.radius_anim_percentage = 1
        self.room.persons.append(self)
    def new_random_pos(self):
        return [0.1+np.random.random()*(self.room.actual_size[0]-0.2), 0.1+np.random.random()*(self.room.actual_size[1]-0.2)]
    def wiggle(self):
        factor = 1
        self.position[0] += np.random.random()*(factor)
        self.position[1] += np.random.random()*(factor)
        self.position[0] -= np.random.random()*(factor)
        self.position[1] -= np.random.random()*(factor)
    def register(self):
        colors = {"v": 0.1, "i": 0.2, "c": 0.3, "d": 0.4}
        color = colors[self.status]
        self.room.draw_data[0].append(self.position[0])
        self.room.draw_data[1].append(self.position[1])
        self.room.draw_data[2].append(color)
        if self.status == "i":
            self.room.draw_data2[0].append(self.position[0])
            self.room.draw_data2[1].append(self.position[1])
            self.room.draw_data2[2].append(((self.radius*self.radius_anim_percentage)**2)*(self.room.scale**2)*radius_to_sice**2)





