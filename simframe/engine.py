from abc import ABCMeta, abstractmethod
import copy
from .agent import Agent, IAgent
from .area import Area, IArea
from .model import Model
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
    def __init__(self, id: str, model: Model):
        self.id = id
        self.neighbors = []
        self.model = model
        self.all_agents = model.agents # this area and neighbor area agents
        self.timestamp = 0  
        self.kdtree = self.set_agents_tree(self.model.agents)

    def set_agents_tree(self, agents: List[IAgent]):
        data = [(agent.position.x, agent.position.y) for agent in agents]
        # kdtree is None if agents data is empty
        kdtree = ss.KDTree(data, leafsize=10) if len(agents) > 0 else None
        return kdtree

    def set_neighbors(self, neighbors):
        self.neighbors = neighbors

    def get_agents(self):
        return self.model.agents

    def step(self):
        # update agents in this area
        self.model.agents = []
        for agent in self.all_agents:
            if self.model.env.area.is_in(agent):
                self.model.agents.append(agent)

        # get interaction agents
        for agent in self.model.agents:
            r = agent.interaction_range
            interaction_agents = []
            if self.kdtree != None:
                interaction_indices = self.kdtree.query_ball_point((agent.position.x, agent.position.y), r)
                interaction_agents = [self.all_agents[idx] for idx in interaction_indices]
            agent.step(interaction_agents)
        self.model.step()
        self.timestamp += 1
        #return {"timestamp": self.timestamp, "id": self.id, "agents": self.model.agents, "area": self.model.env.area}

    async def poststep(self):
        # async await is used by design pattern : https://docs.ray.io/en/latest/ray-design-patterns/concurrent-operations-async-actor.html
        # get neighbor area agents
        refs = []
        for engine in self.neighbors:
            refs.append(engine.get_agents.remote())
        neighbor_agents = [data for result in refs for data in await result]
        
        # update agents kdtree
        self.all_agents = copy.deepcopy(neighbor_agents)
        self.all_agents.extend(self.model.agents)
        self.kdtree = self.set_agents_tree(self.all_agents)




