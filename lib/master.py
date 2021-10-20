from abc import ABCMeta, abstractmethod
import random
from typing import List
from .engine import Engine
from .agent import Agent, Position
from .area import Area
import ray

class Master:
    def __init__(self, config):
        self.config = config
        self.engines: List[Engine] = []

    def prepare(self):
        area_num = 3
        for i in range(area_num):
            # area
            area = Area(
                start_x=i*100,
                end_x=(i+1)*100,
                start_y=0,
                end_y=100
            )
            # agents
            agents = []
            agent_num = 2
            for k in range(agent_num):
                position = Position(
                    x=area.start_x + (area.end_x-area.start_x) * random.random(),
                    y=area.start_y + (area.end_y-area.start_y) * random.random()
                )
                agents.append(Agent("{}-{}".format(i, k), position))
            # engine
            neighbors = self.engines
            self.engines.append(Engine.remote(str(i), neighbors, area, agents))

    def run(self):
        step_num = 10
        for i in range(step_num):
            wip_engines = [engine.step.remote(i) for engine in self.engines]
            results = ray.get(wip_engines)
            print(results)
            print("Finished All Engines Step {}".format(i))

