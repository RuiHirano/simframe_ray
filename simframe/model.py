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

class Model:
    def __init__(self, agents: List[Agent],  environment: Environment, step_num: int,):
        self.env = environment
        self.agents = agents
        self.step_num = step_num


    
