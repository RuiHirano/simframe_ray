from abc import ABCMeta, abstractmethod
import random
from typing import List
from lib.agent import IAgent
from lib.engine import Engine
from lib.agent import Agent, Position
from lib.area import IArea, Area
import ray
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import os
import datetime

class Environment:
    def __init__(self):
        self.area = Area(
            start_x=0,
            end_x=100,
            start_y=0,
            end_y=100
        )
        self.agents = []
        self.step_num = 0

    def set_area(self, area: IArea):
        self.area = area
    
    def set_agents(self, agents: List[IAgent]):
        self.agents = agents

    def set_step_num(self, step_num: int):
        self.step_num = step_num

    def add_agent(self, agent: IAgent):
        self.agents.append(agent)

    def add_agents(self, agents: List[IAgent]):
        self.agents.extend(agents)

