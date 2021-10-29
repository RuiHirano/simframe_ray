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
    def prestep(self, i):
        pass
    @abstractmethod
    def step(self, i):
        pass
    @abstractmethod
    def poststep(self, i):
        pass
    @abstractmethod
    def get_agents(self, i):
        pass
    @abstractmethod
    def set_neighbors(self, neighbors):
        pass

@ray.remote(num_cpus=1)
class Engine:
    def __init__(self, id: str, type: str, area: IArea, agents: List[IAgent]):
        self.id = id
        self.type = type
        self.neighbors = []
        self.area = area
        self.agents = agents
        self.all_agents = agents # this area and neighbor area agents
        self.timestamp = 0  
        self.kdtree = self.set_agents_tree(self.agents)

    def set_agents_tree(self, agents: List[IAgent]):
        data = [(agent.position.x, agent.position.y) for agent in agents]
        # kdtree is None if agents data is empty
        kdtree = ss.KDTree(data, leafsize=10) if len(agents) > 0 else None
        return kdtree

    def set_neighbors(self, neighbors):
        self.neighbors = neighbors

    def get_agents(self):
        return self.agents

    def step(self):
        # update agents in this area
        self.agents = []
        for agent in self.all_agents:
            if self.area.is_in(agent):
                if self.type == "NonSeparate":
                    self.agents.append(agent)
                elif self.type == "Person":
                    if agent.type == self.type:
                        self.agents.append(agent)
                elif self.type == "Weather":
                    if agent.type == "RAIN" or agent.type == "SUNNY":
                        self.agents.append(agent)

        # get interaction agents
        for agent in self.agents:
            r = agent.interaction_range
            interaction_agents = []
            if self.kdtree != None:
                interaction_indices = self.kdtree.query_ball_point((agent.position.x, agent.position.y), r)
                interaction_agents = [self.all_agents[idx] for idx in interaction_indices]
            agent.step(interaction_agents)
        #print("Area: {}, Agent Num: {}".format(self.area.id, len(self.agents)))
        self.timestamp += 1
        #return {"timestamp": self.timestamp, "id": self.id, "agents": self.agents, "area": self.area}

    async def poststep(self):
        # async await is used by design pattern : https://docs.ray.io/en/latest/ray-design-patterns/concurrent-operations-async-actor.html
        # get neighbor area agents
        refs = []
        for engine in self.neighbors:
            refs.append(engine.get_agents.remote())
        neighbor_agents = [data for result in refs for data in await result]
        
        # update agents kdtree
        self.all_agents = copy.deepcopy(neighbor_agents)
        self.all_agents.extend(self.agents)
        self.kdtree = self.set_agents_tree(self.all_agents)




