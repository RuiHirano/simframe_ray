from simframe import IAgent, Agent, Position
from typing import List
import time
class Person(Agent):
    def __init__(self, id: str, position: Position):
        super().__init__(id, position, type="Person")
        self.interaction_range = 10

    #def step(self, interaction_agents: List[IAgent]):
    #    self.position.set_x(self.position.x - 5)
    #    self.position.set_y(self.position.y + 5)
    #    #print("Step Agent (ID: {}) Pos: X:{}, Y: {}".format(self.id, self.position.x, self.position.y))

    def step(self, interaction_agents: List[IAgent]):
        time.sleep(0.005)
        #print(interaction_agents)
        type = self.majorityWeather(interaction_agents)
        #print(type)
        if type == "RAIN":
            self.position.set_x(self.position.x-2)
            self.position.set_y(self.position.y+2)
        else:
            self.position.set_x(self.position.x - 5)
            self.position.set_y(self.position.y + 5)
        #print("Step Agent (ID: {}) Pos: X:{}, Y: {}".format(self.id, self.position.x, self.position.y))

    def majorityWeather(self, agents):
        d = {"RAIN": 0, "SUNNY": 0}
        for agent in agents:
            if agent.type == "RAIN":
                #print("rain")
                d["RAIN"] += 1
            elif agent.type == "SUNNY":
                d["SUNNY"] += 1
        return "RAIN" if d["RAIN"] > d["SUNNY"] else "SUNNY"