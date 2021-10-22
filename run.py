from lib.master import Master
from lib.area import Area
from lib.environment import Environment
from lib.agent import Agent, Position
from model import Car, Person, Weather
import ray 
import os
import random
import time

RAY_CLUSTER_HOST = os.environ.get('RAY_CLUSTER_HOST')
print("Head Address: ", RAY_CLUSTER_HOST)

def wait_for_nodes(expected):
    # Wait for all nodes to join the cluster.
    while True:
        resources = ray.cluster_resources()
        node_keys = [key for key in resources if "node" in key]
        num_nodes = sum(resources[node_key] for node_key in node_keys)
        if num_nodes < expected:
            print("{} nodes have joined so far, waiting for {} more.".format(
                num_nodes, expected - num_nodes))
            time.sleep(1)
        else:
            break

if __name__ == "__main__":
    if RAY_CLUSTER_HOST:
        ray.init(address=RAY_CLUSTER_HOST)
        wait_for_nodes(3)
    else:
        ray.init()

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

    '''for i in range(int(area.end_x-area.start_x)):
        for k in range(int(area.end_y-area.start_y)):
            position = Position(
                x=area.start_x + i,
                y=area.start_y + k
            )
            agents.append(Weather(str(k), position))'''

    env = Environment()
    env.set_area(area)
    env.set_agents(agents)
    env.set_step_num(50)
    master = Master(env)
    master.prepare()
    master.run()