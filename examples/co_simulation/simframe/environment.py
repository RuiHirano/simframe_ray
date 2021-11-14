from abc import ABCMeta, abstractmethod
import random
from typing import List
from .agent import IAgent
from .engine import Engine
from .agent import Agent, Position
from .area import IArea, Area
import ray
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import os
import datetime

class Environment:
    def __init__(self):
        self.area = Area(
            id="environment",
            start_x=0,
            end_x=100,
            start_y=0,
            end_y=100
        )

    def set_area(self, area: IArea):
        self.area = area
    
