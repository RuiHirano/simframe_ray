from simframe import IAgent, Agent, Position
from typing import List
import random

class Weather(Agent):
    def __init__(self, id: str, position: Position):
        self.weather_type = "SUNNY" if position.x > 100 and position.y > 150 else "RAIN"
        super().__init__(id, position, type=self.weather_type)
        self.interaction_range = 10
        self.color = "orange" if self.weather_type == "SUNNY" else "blue"

    def step(self, interaction_agents: List[IAgent]):
        #type = self.majorityWeather(interaction_agents)
        rate = self.rateWeather(interaction_agents)
        #if type != self.weather_type:
        #self.weather_type = type if random.random() < rate else self.weather_type
        if self.weather_type == "SUNNY":
            self.weather_type = "RAIN" if random.random() < rate else self.weather_type
        else:
            self.weather_type = "SUNNY" if random.random() < rate else self.weather_type
        self.color = "orange" if self.weather_type == "SUNNY" else "blue"
        self.type = self.weather_type
        #print(len(interaction_agents), type, self.weather_type, self.color)
        #self.position.set_x(self.position.x + 10)
        #self.position.set_y(self.position.y + 5)
        #print("Step Agent (ID: {}) Pos: X:{}, Y: {}".format(self.id, self.position.x, self.position.y))

    def majorityWeather(self, agents):
        """
        :type nums: List[int]
        :rtype: int
        """
        d = {"RAIN": 0, "SUNNY": 0}
        for agent in agents:
            if agent.type == "SUNNY" or agent.type == "RAIN":
                if agent.weather_type == "RAIN":
                    d["RAIN"] += 1
                else:
                    d["SUNNY"] += 1
        return "RAIN" if d["RAIN"] > d["SUNNY"] else "SUNNY"
    
    def rateWeather(self, agents):
        """
        :type nums: List[int]
        :rtype: int
        """
        d = {"RAIN": 0, "SUNNY": 0}
        for agent in agents:
            if agent.type == "SUNNY" or agent.type == "RAIN":
                if agent.weather_type == "RAIN":
                    d["RAIN"] += 1
                else:
                    d["SUNNY"] += 1
        if (d["SUNNY"]+d["RAIN"]) == 0:
            return 0
        elif self.weather_type == "SUNNY":
            return d["RAIN"] / (d["SUNNY"]+d["RAIN"])
        else:
            return d["SUNNY"] / (d["SUNNY"]+d["RAIN"])