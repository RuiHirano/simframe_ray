from simframe import IAgent, Agent, Position
from typing import List

class Person(Agent):
    def __init__(self, id: str, position: Position):
        super().__init__(id, position, type="Person")
        self.interaction_range = 5
        self.color = "green"

    def step(self, interaction_agents: List[IAgent]):
        type = self.majorityWeather(interaction_agents)
        if type == "RAIN":
            self.position.set_x(self.position.x - 2)
            self.position.set_y(self.position.y + 2)
        else:
            self.position.set_x(self.position.x - 5)
            self.position.set_y(self.position.y + 5)
        #print("Step Agent (ID: {}) Pos: X:{}, Y: {}".format(self.id, self.position.x, self.position.y))

    def majorityWeather(self, agents):
        d = {"RAIN": 0, "SUNNY": 0}
        for agent in agents:
            if agent.type == "SUNNY" or agent.type == "RAIN":
                if agent.weather_type == "RAIN":
                    d["RAIN"] += 1
                else:
                    d["SUNNY"] += 1
        return "RAIN" if d["RAIN"] > d["SUNNY"] else "SUNNY"