from simframe import IAgent, Agent, Position
from typing import List
import random
class Weather(Agent):
    def __init__(self, id: str, position: Position):
        self.type = "SUNNY" if position.x < 200 and position.y < 200 else "RAIN"
        super().__init__(id, position, type=self.type)
        print(self.type)
        self.color = "orange" if self.type == "SUNNY" else "blue"
        self.interaction_range = 10

    def step(self, interaction_agents: List[IAgent]):
        #type = self.majorityWeather(interaction_agents)
        rate = self.rateWeather(interaction_agents)
        #if type != self.type:
        #self.type = type if random.random() < rate else self.type
        if self.type == "SUNNY":
            self.type = "RAIN" if random.random() < rate else self.type
        else:
            self.type = "SUNNY" if random.random() < rate else self.type
        self.color = "orange" if self.type == "SUNNY" else "blue"
        #self.type = self.type
        #print(len(interaction_agents), type, self.type, self.color)
        #self.position.set_x(self.position.x + 10)
        #self.position.set_y(self.position.y + 5)
        #print("Step Agent (ID: {}) Pos: X:{}, Y: {}".format(self.id, self.position.x, self.position.y))
    
    def rateWeather(self, agents):
        """
        :type nums: List[int]
        :rtype: int
        """
        d = {"RAIN": 0, "SUNNY": 0}
        for agent in agents:
            if agent.type == "RAIN":
                d["RAIN"] += 1
            elif agent.type == "SUNNY":
                d["SUNNY"] += 1
        if (d["SUNNY"]+d["RAIN"]) == 0:
            return 0
        elif self.type == "SUNNY":
            return d["RAIN"] / (d["SUNNY"]+d["RAIN"])
        else:
            return d["SUNNY"] / (d["SUNNY"]+d["RAIN"])