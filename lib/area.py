from abc import ABCMeta, abstractmethod
from .agent import Agent
from typing import List

class IArea(metaclass=ABCMeta):
    @abstractmethod
    def get(self):
        pass
    
class Area(IArea):
    def __init__(self, start_x: float, start_y: float, end_x: float, end_y: float):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y

    def get(self):
        pass

        