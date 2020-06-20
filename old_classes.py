from mpl_toolkits.axes_grid1 import Divider, Size
import numpy as np
import random



class room:
    def __init__(self):
        self.ax = None
        self.divider = None
        self.location_on_screen = (0.5,0)
        self.size_on_screen = (1,1)
        self.actual_size = (3,3)
        self.members = 0
        self.scale = 1
        self.border = 0.1
        self.draw_data = [[],[],[]]
        self.draw_data2 = [[],[],[]]
    def get_divider(self, fig):
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
        self.ax.get_xaxis().set_visible(False)
        self.ax.get_yaxis().set_visible(False)
        self.ax.set_xlim(0, self.actual_size[0])
        self.ax.set_ylim(0, self.actual_size[1])
    def clear_room(self):
        self.draw_data = [[],[],[]]
        self.draw_data2 = [[],[], []]
    def draw(self):
        self.ax.scatter(self.draw_data[0], self.draw_data[1], c = self.draw_data[2], s = 10/self.scale)
        self.ax.scatter(self.draw_data2[0], self.draw_data2[1], sizes = self.draw_data2[2], c = "r", alpha= 0.3)



class Person:
    def __init__(self, room):
        self.status = random.choice(["v", "i", "c", "d"])
        self.room = room
        self.position = (0.1+np.random.random()*(self.room.actual_size[0]-0.2), 0.1+np.random.random()*(self.room.actual_size[1]-0.2))
    def register(self):
        colors = {"v": "blue", "i": "red", "c": "green", "d": "k"}
        color = colors[self.status]
        self.room.draw_data[0].append(self.position[0])
        self.room.draw_data[1].append(self.position[1])
        self.room.draw_data[2].append(color)
        if self.status == "i":
            self.room.draw_data2[0].append(self.position[0])
            self.room.draw_data2[1].append(self.position[1])
            self.room.draw_data2[2].append(100/self.room.scale)





