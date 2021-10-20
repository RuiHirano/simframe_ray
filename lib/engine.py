from abc import ABCMeta, abstractmethod

import copy
from .agent import Agent, IAgent
from .area import Area, IArea
from typing import List
import ray
import scipy.spatial as ss
import time

class IEngine(metaclass=ABCMeta):
    @abstractmethod
    def step(self, i):
        pass
    @abstractmethod
    def get_agents(self, i):
        pass

@ray.remote(num_cpus=1)
class Engine:
    def __init__(self, id: str, neighbors: List[IEngine], area: IArea, agents: List[IAgent]):
        self.id = id
        self.neighbors = neighbors
        self.area = area
        self.agents = agents
        self.all_agents = agents # this area and neighbor area agents
        self.timestamp = 0  
        self.kdtree = self.set_agents_tree(self.agents)

    def set_agents_tree(self, agents: List[IAgent]):
        data = [(agent.position.x, agent.position.y) for agent in agents]
        kdtree = ss.KDTree(data, leafsize=10)
        return kdtree

    def get_agents(self):
        return self.agents

    def step(self, i):
        print("Neighbor Engine: {}. {}", self.id, self.neighbors)
        print("Engine ID {}, Timestamp: {}, {}".format(self.id, self.timestamp, i))
        # get neighbor area agents
        neighbor_agents = []
        for engine in self.neighbors:
            neighbor_agents.extend(ray.get(engine.get_agents.remote()))

        # update agents kdtree
        data = copy.deepcopy(neighbor_agents)
        data.extend(self.agents)
        self.all_agents = data
        self.kdtree = self.set_agents_tree(self.all_agents)

        # get interaction agents
        for agent in self.agents:
            r = agent.interaction_range
            interaction_indices = self.kdtree.query_ball_point((agent.position.x, agent.position.y), r)
            interaction_agents = [self.all_agents[idx] for idx in interaction_indices]
            agent.step(interaction_agents)
        self.timestamp += 1
        return i