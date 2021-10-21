from abc import ABCMeta, abstractmethod
from typing import List

# 抽象クラス
class IAgent(metaclass=ABCMeta):
    @abstractmethod
    def step(self, neighbors):
        pass

class Position:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def set_x(self, x):
        self.x = x
    
    def set_y(self, y):
        self.y = y

class Agent(IAgent):
    def __init__(self, id: str, position: Position):
        self.id = id
        self.position = position
        self.interaction_range = 1

    def step(self, neighbors: List[IAgent]):
        self.position.set_x(self.position.x + 10)
        print("Step Agent (ID: {}) Pos: X:{}, Y: {}".format(self.id, self.position.x, self.position.y))

