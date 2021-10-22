from abc import ABCMeta, abstractmethod
import copy
from lib.agent import Agent, IAgent
from lib.area import Area, IArea
from typing import List
import ray
import scipy.spatial as ss

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
    def __init__(self, id: str, area: IArea, agents: List[IAgent]):
        self.id = id
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

    def prestep(self):
        print("Prestep: {}".format(self.id))
        # update agents in this area
        self.agents = []
        for agent in self.all_agents:
            if self.area.is_in(agent):
                self.agents.append(agent)

    def step(self):
        # get interaction agents
        for agent in self.agents:
            r = agent.interaction_range
            interaction_agents = []
            if self.kdtree != None:
                interaction_indices = self.kdtree.query_ball_point((agent.position.x, agent.position.y), r)
                interaction_agents = [self.all_agents[idx] for idx in interaction_indices]
            agent.step(interaction_agents)
        self.timestamp += 1
        return {"timestamp": self.timestamp, "id": self.id, "agents": self.agents, "area": self.area}

    async def poststep(self):
        # async await is used by design pattern : https://docs.ray.io/en/latest/ray-design-patterns/concurrent-operations-async-actor.html
        print("Poststep: (ID: {}), timetamp: {}".format(self.id, self.timestamp), self.neighbors)
        # get neighbor area agents
        refs = []
        for engine in self.neighbors:
            refs.append(engine.get_agents.remote())
        neighbor_agents = [data for result in refs for data in await result]
        
        # update agents kdtree
        self.all_agents = copy.deepcopy(neighbor_agents)
        self.all_agents.extend(self.agents)
        self.kdtree = self.set_agents_tree(self.all_agents)




