from lib.agent import IAgent, Agent, Position
from typing import List

class Person(Agent):
    def __init__(self, id: str, position: Position):
        super().__init__(id, position, type="Person")
        self.interaction_range = 1

    def step(self, interaction_agents: List[IAgent]):
        for in_agent in interaction_agents:
            if in_agent.type == "Weather":
                self.position.set_x(self.position.x - 2)
                self.position.set_y(self.position.y + 2)
                return
        
        self.position.set_x(self.position.x - 5)
        self.position.set_y(self.position.y + 5)
        #print("Step Agent (ID: {}) Pos: X:{}, Y: {}".format(self.id, self.position.x, self.position.y))

