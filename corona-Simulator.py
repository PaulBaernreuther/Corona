"""Program of Paul Bärnreuther and Jonas Kleinöder.
It is a simulator of an epidemic. It automatically allows for simulation of how a pathogen spreads, while taking advanced problems into account like for example:
*every person behaves differently.
*the healthcare system can be overburdened.
It has a few sub-scenarios, which include:
*multiple room, where one cannot infect another through a room, but a few persons who can jump between rooms.
*a supermarket, where everybody needs to go at some point.
*every person has a probability to be sent off to quarantine, where they can no longer infect others.
Note that this program does not aim to simulate actual 2D space, rather it simulates a 'contact-space'
where closeness means means how close two persons are to having physical contact, rather than actual physical closeness.
this has the advantage of more easily calculable while staying mostly true to reality (compared to the alternative solution of just simulating actual 2D space) """
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider
import time

import matplotlib.animation as anim
from rooms import *

default_dict = {"members": [300,1,500,1],
                "number of infected": [1,1,50,1],
                "deathrate": [0.1,0.1,1,0.1],
                "deathrate without healthcare": [0.5,0.5,1,0.05],
                "number of infected days": [7,1,21,1],
                "infection rate": [0.2,0.1,1,0.1],
                "shape": [50,1,100,1],
                "radius": [2,0.5,5,0.1],
                "speed": [0.5,0.1,5,0.1],
                "healthcare max": [0.1,0.01,1,0.01],
                "chance for bad infection": [0.05,0.01,1,0.01],
                "percentage of jumpers": [0.01,0.01,1,0.01],
                "time between jumps": [7,1,10,1],
                "time between purchases": [7,1,14,1],
                "chance for symptoms": [0.6,0.1,1,0.1]}
STEP  = False
PLAY = True
APPLY = False


class scenario:
    """this is the biggest class, governing the other two classes room and person (more on those in the file rooms.
    here you can adjust all the values which influence the simulation:
    frames_per_day is the amount of moving that is beeing done before the next infection step takes place. imagine frames as hours and time steps as days.
    number_infected is the staring number of infected persons per room
    deathrate is the chance a person dies after beeing infected, while having access to healthcare
    deathrate_without_healthcare is the same, just without healtcare
    max_infected_time is how many time steps a person is going to be infected
    infection_rate is the percentage that a person is infected, when a vulnerable person and an infecete person a close enough to each other
    shape is the shape of the rooms
    members is the amount of persons per room
    radius is the radius in which person infects (or get infected by) persons (figuratively speaking a bigger radius translates to a higher amount of (the almost same) persons met)
    speed is the distance that a person moves per update (figuratively speaking a higher speed translates to a higher amount of different persons met)
    healthcare_max is the percentual amount of members. it represents the amount of people that can be treated by the healthcare system simultaniously
    bed_chance is the chance that a given person needs healthcare in order to have high chances of survival when infected
    """
    def __init__(self, frames_per_day = 12, number_of_rooms = 1, number_infected = 1, deathrate = 0.1, deathrate_without_healthcare = 0.5, max_infected_time = 7, infectionrate = 0.2, shape = (50,50), members = 300, radius = 2, speed = 0.5, healthcare_max = 0.1, bed_chance = 0.05):
        self.number_of_rooms = number_of_rooms
        self.shape = shape
        self.members = members
        self.number_infected = number_infected
        self.deathrate = deathrate
        self.deathrate_without_healthcare = deathrate_without_healthcare
        self.max_infected_time = max_infected_time
        self.infectionrate = infectionrate
        self.radius = radius
        self.speed = speed
        self.healthcare_max = int(members * healthcare_max * number_of_rooms)
        self.bed_chance = bed_chance

        self.rooms = []
        self.opt_arangement = 0,0
        self.current_arangement = [0,0]
        self.data = {"i": [], "v": [], "c": [], "d": []}
        self.list_of_infected = []
        self.beds = self.healthcare_max
        self.frames_per_day = frames_per_day
        self.current_frame = 0
        self.variables = [self.members, self.number_infected, self.deathrate, self.deathrate_without_healthcare,
                          self.max_infected_time, self.infectionrate, self.shape, self.radius, self.speed,
                          self.healthcare_max, self.bed_chance]
        self.names = ["members",
                "number of infected",
                "deathrate",
                "deathrate without healthcare",
                "number of infected days",
                "infection rate",
                "shape",
                "radius",
                "speed",
                "healthcare max",
                "chance for bad infection",
                "percentage of jumpers",
                "time between jumps",
                "time between purchases",
                "chance for symptoms"]

    def find_opt_arangement(self):
        """finds the optimal arangement for the rooms, that are beeing plotted"""
        a, b = fig.get_size_inches()
        return find_opt_arangement(self.number_of_rooms, ratio=(self.shape[1] * a / 2) / (self.shape[0] * b))
    def create_rooms(self):
        """initializes the rooms and persons within them"""
        i,j = self.find_opt_arangement()
        self.current_arangement = [i,j]
        for l in range(self.number_of_rooms):
            newroom = Room(number_infected=self.number_infected, act_size = self.shape, members = self.members)
            newroom.show_on_fig(fig, i, 2 * j, (1 + (l // j)) * j + l + 1)
            newroom.compute_scale(fig)
            the_infected = random.sample(range(self.members), self.number_infected)
            those_who_will_need_bed = random.sample(range(self.members), int(self.bed_chance * self.members))
            for m in range(self.members):
                person = Person(newroom, max_infected_time=self.max_infected_time, deathrate=self.deathrate, deathrate_without_healthcare=self.deathrate_without_healthcare, infectionrate= self.infectionrate, radius = self.radius, speed=self.speed)
                if m in those_who_will_need_bed:
                    person.will_need_bed = True
                if m in the_infected:
                    person.status = "i"
                person.register()
            self.rooms.append(newroom)
    def new_room(self, size = None):
        """adds another room to the already existing ones"""
        if size:
            shape = size
        else:
            shape = self.shape
        specialroom = Room(number_infected=self.number_infected, act_size = shape, members = 0)
        self.number_of_rooms += 1
        i, j = self.find_opt_arangement()
        for l, room in enumerate(self.rooms):
            room.ax.remove()
            room.show_on_fig(fig, i, 2 * j, (1 + (l // j)) * j + l + 1)
        l = self.number_of_rooms - 1
        specialroom.show_on_fig(fig, i, 2 * j, (1 + (l // j)) * j + l + 1)
        self.current_arangement = [i, j]
        self.rooms.append(specialroom)
        animation._blit = False
        return specialroom
    def update_room_axes(self):
        """determines whther current arangement of rooms is still optimal"""
        i,j = self.find_opt_arangement()
        if i != self.current_arangement[0] or j != self.current_arangement[1]:
            for l, room in enumerate(self.rooms):
                room.ax.remove()
                room.show_on_fig(fig, i, 2 * j, (1 + (l // j)) * j + l + 1)
            self.current_arangement = [i, j]
            animation._blit = False
    def draw_all_rooms(self):
        """draws all rooms :D"""
        for thisroom in self.rooms:
            thisroom.draw()
    def update_scatters(self):
        """update function, which makes every person move (and plots it(kinda))"""
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
        """updates the data of the persons, ie.: who's infected, vulnerable, cured, deceased"""
        for char in ["i", "v", "c", "d"]:
            self.data[char].append(0)
        for room in self.rooms:
            room.update_data()
            for char in ["i", "v", "c", "d"]:
                self.data[char][-1] += room.data[char][-1]

    def update_relative_graph(self):
        """updates the graph on the left, which shows the number of infected, cured vulnerable and deceased persons"""
        out = {}
        size = (len(self.data["i"]))
        for charlist in ["i", ["v","i"], ["c","v", "i"], ["d","c", "v", "i"]]:
            out[charlist[0]] = np.array([0] + [sum([self.data[char][item] for char in charlist]) for item in range(size)] + [0])
        return np.array([0] + [i for i in range(size)] + [len(self.data["i"]) - 1]), out

    def calculate_infected(self):
        """calculates which persons are now infected on a room, by room basis"""
        for room in self.rooms:
            room.calculate_infected(self.list_of_infected)

    def calculate_beds(self):
        """calculates haw many places there are left in the healthcare system"""
        for prsn in self.list_of_infected.copy():
            if prsn.will_need_bed and self.beds > 0:
                self.beds -= 1
                prsn.is_in_bed = True
            self.list_of_infected.remove(prsn)

    def calculate_death(self):
        """calculates which persons are now deceased or cured on a room, by room basis"""
        for room in self.rooms:
            self.beds = room.calculate_death(self.beds)

    def time_step(self):
        """calls all updating functions, every frames_per_day updates (that it only does it that often is not clear here, but in the function update)"""
        self.calculate_infected()
        self.calculate_beds()
        self.calculate_death()
        self.update_data()
        return self.update_relative_graph()

    def jump(self, prsn, codomain, pos = None):
        """makes one person (prsn) move from their room to another room (codmain) and if given to a certain position in that room (pos)"""
        prsn.room.persons.remove(prsn)
        codomain.persons.append(prsn)
        prsn.room = codomain
        if not pos:
            prsn.position = prsn.new_random_pos()
        else:
            prsn.position = pos
        prsn.room.members -= 1
        codomain.members += 1

    def update_variables(self):
        self.members = current_values[self.names[0]]
        self.number_infected = current_values[self.names[1]]
        self.deathrate = current_values[self.names[2]]
        self.deathrate_without_healthcare = current_values[self.names[3]]
        self.max_infected_time = current_values[self.names[4]]
        self.infectionrate = current_values[self.names[5]]
        self.shape = current_values[self.names[6]]
        self.radius = current_values[self.names[7]]
        self.speed = current_values[self.names[8]]
        self.healthcare_max = current_values[self.names[9]]
        self.bed_chance = current_values[self.names[10]]



class Cluster(scenario):
    """a sub-scenario: it entails the inclusion of multiple rooms, which are separated from each other, by borders not crossable by the pathogen.
    but there is also persons called jumpers, who can move between rooms on occasion"""
    def __init__(self, jumpy_percentage = 0.01, jumptime = 7, *args, **kwargs):
        """jumpy_percentage is the percentage of persons who will later be able to 'jump'
        jumptime is the time each 'jumper' takes inbetween jumps
        time_since_jump is the time since a person has jumped last"""
        super().__init__(*args, **kwargs)
        self.jumpy_percentage = jumpy_percentage
        self.jumptime = jumptime
        self.time_since_jump = 0
        self.variables.append(self.jumpy_percentage)
        self.variables.append(self.jumptime)

    def create_rooms(self):
        """the room initialization needs to be updated with the new variables"""
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
        """every movement update needs to be updated, so that jumpers actually jump"""
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

    def update_variables(self):
        super().update_variables()
        self.jumpy_percentage = current_values[self.names[11]]
        self.jumptime =current_values[self.names[12]]


class Supermarket(scenario):
    """a sub-scenario: it entails the inclusion of a room called supermarket, where every person needs to go in certain intervals"""
    def __init__(self, purchase_interval = 7, *args, **kwargs):
        """shopping_time is the time every person is in the market"""
        super().__init__(*args, **kwargs)
        self.shopping_time = 1
        self.purchase_interval = purchase_interval
        self.variables.append(self.shopping_time)

    def create_rooms(self):
        """purchase_interval is the time a person takes until they go to the supermarket again
        room_of_origin is the room a person comes from (so that we can get them back to their neighbourhood)
        home is the coordinates where a person comes from (so that we can get them back to their house)"""
        super().create_rooms()
        for room in self.rooms:
            for prsn in room.persons:
                prsn.purchase_interval = self.purchase_interval + int(random.random() * 0.5 * self.purchase_interval - 0.25 * self.purchase_interval)
                prsn.time_since_purchase = int(random.random() * prsn.purchase_interval)
                prsn.time_in_market = 0
                prsn.room_of_origin = prsn.room
                prsn.home = prsn.position
        self.market = self.new_room(size = [10,30])
        self.market.ax.set_title("Supermercado")

    def update_scatters(self):
        """makes persons acutally go to the supermarket and home again"""
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

    def update_variables(self):
        super().update_variables()
        self.purchase_interval = current_values[self.names[13]]


class Quarantine(scenario):
    """a sub-scenario: it entails the inclusion of a room called quarantine.
    every person gets a chance to show symptoms, when they do they get moved to the quarantine room until they no longer infected."""
    def __init__(self, symptom_chance = 0.6, *args, **kwargs):
        """symptom_chance is the chance that a person that is infected shows symptoms (and is therefore put in quarantine)"""
        super().__init__(*args, **kwargs)
        self.symptom_chance = symptom_chance
        self.variables.append(self.symptom_chance)

    def create_rooms(self):
        """just like in the other sub-scenarios we need to initialize this"""
        super().create_rooms()
        for room in self.rooms:
            for prsn in room.persons:
                prsn.room_of_origin = prsn.room
                prsn.home = prsn.position
                if random.random() <= self.symptom_chance:
                    prsn.symptomatic = True
                else:
                    prsn.symptomatic = False
        self.quarantine_room = self.new_room()
        self.quarantine_room.ax.set_title("Quarantine")

    def update_scatters(self):
        """this actually moves persons with symptoms into quarantine and to their homes again if no longer infected"""
        for room in self.rooms:
            for prsn in room.persons:
                if prsn.status == "i"and prsn.symptomatic and prsn.room is not self.quarantine_room:
                    self.jump(prsn, self.quarantine_room)
        for prsn in self.quarantine_room.persons:
            if prsn.status == "c" or prsn.status == "d":
                self.jump(prsn, prsn.room_of_origin, prsn.home)
        return super().update_scatters()

    def update_variables(self):
        super().update_variables()
        self.symptom_chance = current_values[self.names[14]]



scenario_dict = {"scenario": scenario, "Cluster": Cluster, "Supermarket": Supermarket, "Quarantine": Quarantine}


fig = plt.figure(figsize=(11,4))
fig.patch.set_facecolor('#123456')
fig.patch.set_alpha(0.7)
ax = fig.add_subplot(2,2,1)



k = 9
newscenario = Supermarket()

start = time.time()
def update(frame_number):
    """is called at ever update of the plot and therefore serves as the backbone of the animation loop"""
    global newscenario
    animation._blit = True
    global PLAY
    global STEP
    global APPLY
    if APPLY:
        APPLY = False
        animation._blit = False
        newscenario = scenario_dict[current_scenario]()
        newscenario.update_variables()
        newscenario.create_rooms()
        newscenario.draw_all_rooms()
    if not PLAY:
        return []
    if newscenario.current_frame >= newscenario.frames_per_day:
        if STEP:
            PLAY = False
            STEP = False
        newscenario.current_frame = 0
        x, data = newscenario.time_step()
        ax.clear()
        for char in ["d", "c", "v", "i"]:
            ax.fill(x, data[char], c = colors[char])
        ax.plot(x, [newscenario.healthcare_max for i in x], c = "0.5")
    newscenario.update_room_axes()
    newscenario.current_frame += 1
    return newscenario.update_scatters()+[ax]


animation = FuncAnimation(fig, update, interval=1, blit = True)

newscenario.create_rooms()
newscenario.draw_all_rooms()

from matplotlib.widgets import Button, Slider, RadioButtons

buttonscreen = plt.figure(figsize=(5, 5))


def add_room(a):
    newscenario.new_room()


class ClickButton:
    def __init__(self, pos, label="default", func=None):
        i, j, k = pos[0], pos[1], pos[2]
        self.ax = buttonscreen.add_subplot(i, j, k)
        self.label = label
        self.button = Button(self.ax, label=self.label)
        self.func = func
        if func:
            def fun(a):
                return self.func()

            self.button.on_clicked(fun)

    def on_clicked(self, func):
        def fun(a):
            return func()

        self.button.on_clicked(fun)

    def on_clicked_pass_self(self, func):
        def fun(a):
            return func(self)

        self.button.on_clicked(fun)


'''button1 = ClickButton(3,2,1, "A")
button2 = ClickButton(3,2,2, "B")
button3 = ClickButton(3,2,3, "C")'''

number_of_shown_options = 3
current_option = 0
options = [item for item in default_dict.keys()]
current_values = {}
current_scenario = "Standard"

for key in default_dict.keys():
    current_values[key] = default_dict[key][0]

slider_options = []
for i in range(number_of_shown_options):
    key = options[i]
    slider_options.append(
        ClickButton(compute_position(3 * (number_of_shown_options + 4), 2, 2 + i, 0), "Slider " + str(i)))
    slider_options[i].button.label.set_text(key)
    slider_options[i].label = key

up = ClickButton(compute_position(3 * (number_of_shown_options + 4), 6, 1, 1), "previous")
down = ClickButton(compute_position(3 * (number_of_shown_options + 4), 6, number_of_shown_options + 2, 1), "next ")

slider_ax = buttonscreen.add_subplot(9, 2, 4)
slider = Slider(slider_ax, '', 0, 10, valinit=-1, valstep=0.01)
slider.ax.set_xlim(slider.valmin, slider.valmax)

rax = buttonscreen.add_subplot(3, 2, 3)
radio = RadioButtons(rax, ("Standard", "Cluster", "Supermarket", "Quarantine"), active=0)

apply = ClickButton((3, 2, 4), "apply")

reset = ClickButton(compute_position(9, 7, 7, 1), "reset")
play = ClickButton(compute_position(9, 7, 7, 3), "play/pause")
step = ClickButton(compute_position(9, 7, 7, 5), "step")

PLAY = True
STEP = False
current_slider_key = None


def show_slider(slider_option):
    key = slider_option.label
    global current_slider_key
    current_slider_key = key
    slider.label.set_text(key)
    slider.valmin = default_dict[key][1]
    slider.valmax = default_dict[key][2]
    slider.set_val(current_values[key])
    print(current_values[key])
    print(key, slider.valmin, slider.val, slider.valmax)
    slider.ax.set_xlim(slider.valmin, slider.valmax)


for i in range(number_of_shown_options):
    slider_options[i].on_clicked_pass_self(show_slider)


def play_func():
    global PLAY
    if PLAY:
        PLAY = False
    else:
        PLAY = True


def reset_func():
    for key in options:
        current_values[key] = default_dict[key][0]


def step():
    global PLAY
    global STEP
    PLAY = True
    STEP = True


def change_value(var):
    current_values[current_slider_key] = var


def up_func():
    print("going up")
    global current_option
    current_option -= 1
    for i in range(number_of_shown_options):
        text = options[(current_option + i) % len(options)]
        slider_options[i].button.label.set_text(text)
        slider_options[i].label = text


def down_func():
    global current_option
    current_option += 1
    for i in range(number_of_shown_options):
        text = options[(current_option + i) % len(options)]
        slider_options[i].button.label.set_text(text)
        slider_options[i].label = text


up.on_clicked(up_func)
down.on_clicked(down_func)

slider.on_changed(change_value)

plt.show()
