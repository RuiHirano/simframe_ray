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
    
    agent_num_list = [1000, 1000]
    separate_list = [True, False]
    result = [[], []]
    agent_num = 20000
    separate = True
    for k in range(agent_num):
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
        step_num=10,
    ))

    sim = Simulator(sc, separate=separate)
    #start = time.time()
    print("Agent Num: {}, Separate: {}".format(agent_num, separate))
    sim.run()
    #elapsed_time = time.time() - start
    #print("Result: {}, Agent Num: {}, Separate: {}".format(elapsed_time, agent_num, separate))
    #result[n].append(elapsed_time)
        
    '''print("finished")
    import numpy as np
    import matplotlib.pyplot as plt 

    plt.plot([1000, 5000, 10000, 50000, 100000], [0.496, 1.482, 3.160, 21.491, 58.595] ,label="Separate")
    plt.plot([1000, 5000, 10000, 50000, 100000], [0.488, 1.344, 2.440, 20.064, 50.722] ,label="NonSeparate")

    plt.title("Elapsed Time vs Agent Num",fontsize=15)
    plt.xlabel("agents_num",fontsize=13)
    plt.ylabel("elapsed_time",fontsize=13)
    plt.show()'''

