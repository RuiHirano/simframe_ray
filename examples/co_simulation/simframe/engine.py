from abc import ABCMeta, abstractmethod
import copy
from .agent import Agent, IAgent
from .area import Area, IArea
from typing import List
import ray
import scipy.spatial as ss
import time
import socket
import pickle
import threading

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
    def __init__(self, id: str, type: str, area: IArea, agents: List[IAgent], my_address: str, cosim_address: str, port: int, wait=False):
        self.id = id
        self.type = type
        self.neighbors = []
        self.area = area
        self.agents = agents
        self.all_agents = agents # this area and neighbor area agents
        self.timestamp = 0  
        self.kdtree = self.set_agents_tree(self.agents)
        self.my_address = my_address
        self.cosim_address = cosim_address
        self.port = port
        thread = threading.Thread(target=self.listen_co_simulator)
        thread.start()
        print("waiting for ready server: {}:{}".format(self.my_address, self.port))
        time.sleep(2)
        if wait:
            time.sleep(10000)

    def listen_co_simulator(self):
        # pkill -KILL -f ray
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.my_address, self.port))  # IPとポート番号を指定します
        s.listen(5)
        while True:
            clientsocket, address = s.accept()
            #print(f"Connection from {address} has been established!")
            msg = pickle.dumps(self.agents)
            clientsocket.send(msg)
            clientsocket.close()

    def get_co_agents(self):
        #print("get cosim agents: {}:{}".format(self.cosim_address, self.port))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.cosim_address, self.port))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        full_msg = b''
        while True:
            msg = s.recv(4096)
            if len(msg) <= 0:
                break
            full_msg += msg
        agents = pickle.loads(full_msg)
        #print(len(agents))
        #time.sleep(1)
        return agents

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
        self.get_co_agents()
        
        # update agents kdtree
        self.all_agents = copy.deepcopy(neighbor_agents)
        self.all_agents.extend(self.agents)
        self.kdtree = self.set_agents_tree(self.all_agents)




