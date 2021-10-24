from abc import ABCMeta, abstractmethod
from .agent import IAgent
from typing import List

class IArea(metaclass=ABCMeta):
    @abstractmethod
    def is_in(self):
        pass
    
class Area(IArea):
    def __init__(self, id: str, start_x: float, start_y: float, end_x: float, end_y: float):
        self.id = id
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y

    def is_in(self, agent: IAgent):
        x, y = agent.position.x, agent.position.y
        if self.start_x < x and x <= self.end_x and self.start_y < y and y <= self.end_y:
            return True
        return False

        