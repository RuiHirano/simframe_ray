from abc import ABCMeta, abstractmethod
import random
from typing import List
from .agent import IAgent
from .engine import Engine
from .agent import Agent, Position
from .area import IArea, Area
from .environment import Environment
import ray
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import os
import datetime

class ScenarioParameter:
    def __init__(self, 
        agents: List[Agent], 
        environment: Environment,
        step_num: int,
    ):
        self.agents = agents
        self.environment = environment
        self.step_num = step_num
        self._check_param()

    def _check_param(self):
        pass

class Scenario:
    def __init__(self, param: ScenarioParameter):
        self.param = param
        self.env = self.param.environment
        self.agents = self.param.agents
        self.step_num = self.param.step_num


    
