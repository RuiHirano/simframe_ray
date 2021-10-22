from lib.agent import IAgent, Agent, Position
from typing import List

class Person(Agent):
    def __init__(self, id: str, position: Position):
        super().__init__(id, position, type="Person")
        self.interaction_range = 1

    def step(self, interaction_agents: List[IAgent]):
        self.position.set_x(self.position.x - 5)
        self.position.set_y(self.position.y + 5)
        print("Step Agent (ID: {}) Pos: X:{}, Y: {}".format(self.id, self.position.x, self.position.y))

