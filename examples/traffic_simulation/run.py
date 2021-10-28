from simframe import Agent, Position, Environment, Area, Simulator, Model
from agent import Car, Person
import ray 
import os
import random
import time

class MyModel(Model):
    def __init__(self):
        area = Area(
            id="environment",
            start_x=0,
            end_x=300,
            start_y=0,
            end_y=300
        )
        self.env = Environment()
        self.env.set_area(area)

        self.agents = []
        car_num = 20
        for k in range(car_num):
            position = Position(
                x=area.start_x + (area.end_x-area.start_x) * random.random(),
                y=area.start_y + (area.end_y-area.start_y) * random.random()
            )
            self.agents.append(Car(str(k), position))
        
        person_num = 4000
        for k in range(person_num):
            position = Position(
                x=area.start_x + (area.end_x-area.start_x) * random.random(),
                y=area.start_y + (area.end_y-area.start_y) * random.random()
            )
            self.agents.append(Person(str(k), position))


    def step(self):
        #print("model step", len(self.agents))
        pass

if __name__ == "__main__":

    model = MyModel()

    sim = Simulator(model)
    sim.run(iteration=50)
