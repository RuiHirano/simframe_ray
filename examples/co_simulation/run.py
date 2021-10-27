from simframe import Agent, Position, Environment, Area, Scenario, Simulator, ScenarioParameter
from model import Weather, Person
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
    
    person_num = 400
    for k in range(person_num):
        position = Position(
            x=area.start_x + (area.end_x-area.start_x) * random.random(),
            y=area.start_y + (area.end_y-area.start_y) * random.random()
        )
        agents.append(Person(str(k), position))

    for i in range(0, int(area.end_x-area.start_x), 10):
        for k in range(0, int(area.end_y-area.start_y), 10):
            position = Position(
                x=area.start_x + i,
                y=area.start_y + k
            )
            agents.append(Weather(str(k), position))
    env = Environment()
    env.set_area(area)

    sc = Scenario(ScenarioParameter(
        environment=env,
        agents=agents,
        step_num=50,
    ))

    sim = Simulator(sc)
    sim.run()

