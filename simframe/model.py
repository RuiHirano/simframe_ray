from typing import List
from .agent import Agent
from .environment import Environment

class Model:
    def __init__(self):
        self.env = None
        self.agents = None

    def step(self):
        pass
  
    def set_agents(self, agents: List[Agent]):
        self.agents = agents

    def set_env(self, env: Environment):
        self.env = env