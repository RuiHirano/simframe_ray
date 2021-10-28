from simframe import Agent, Position, Environment, Area, Simulator, Model
from model import Car, Person
import ray 
import os
import random
import time

if __name__ == "__main__":
    
    area = Area(
        id="environment",
        start_x=0,
        end_x=300,
        start_y=0,
        end_y=300
    )
    agents = []
    car_num = 20
    for k in range(car_num):
        position = Position(
            x=area.start_x + (area.end_x-area.start_x) * random.random(),
            y=area.start_y + (area.end_y-area.start_y) * random.random()
        )
        agents.append(Car(str(k), position))
    
    person_num = 40
    for k in range(person_num):
        position = Position(
            x=area.start_x + (area.end_x-area.start_x) * random.random(),
            y=area.start_y + (area.end_y-area.start_y) * random.random()
        )
        agents.append(Person(str(k), position))

    env = Environment()
    env.set_area(area)

    model = Model(
        environment=env,
        agents=agents,
        step_num=50,
    )

    sim = Simulator(model)
    sim.run()
