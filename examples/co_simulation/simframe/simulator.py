from abc import ABCMeta, abstractmethod
import random
from typing import List
from .engine import Engine
from .agent import Agent, Position
from .area import Area
from .environment import Environment
from .scenario import Scenario
import ray
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import os
import datetime
import time

import multiprocessing
print("cpu num: ", multiprocessing.cpu_count())

class Simulator:
    def __init__(self, scenario: Environment, my_address: str, cosim_address: str):
        self.my_address = my_address
        self.cosim_address = cosim_address
        self.scenario = scenario
        self.env = scenario.env
        self.engines: List[Engine] = []

    def prepare(self):
        area_width_num = 2
        area_height_num = 2
        engine_grid = [[None for _ in range(area_width_num)] for _ in range(area_height_num)]
        port = 8000
        for k in range(area_height_num):
            for i in range(area_width_num):
                # area
                area = Area(
                    id=str(k)+str(i),
                    start_x=self.env.area.start_x + (self.env.area.end_x-self.env.area.start_x)*(i/area_width_num),
                    end_x=self.env.area.start_x + (self.env.area.end_x-self.env.area.start_x)*((i+1)/area_width_num),
                    start_y=self.env.area.start_y + (self.env.area.end_y-self.env.area.start_y)*(k/area_height_num),
                    end_y=self.env.area.start_y + (self.env.area.end_y-self.env.area.start_y)*((k+1)/area_height_num),
                )

                # agents
                agents = [agent for agent in self.scenario.agents if area.is_in(agent)]

                # engine
                engine_grid[k][i] = Engine.remote(str(k)+str(i), "NonSeparate", area, agents, self.my_address, self.cosim_address, port)
                print("Area: x:{}-{}, y:{}-{}, agents: {}".format(area.start_x, area.end_x, area.start_y, area.end_y, len(agents)))
                port += 1

        for k in range(area_height_num):
            for i in range(area_width_num):
                engine = engine_grid[k][i]
                neighbors = []
                if i != 0:
                    neighbors.append(engine_grid[k][i-1])
                if i != area_width_num-1:
                    neighbors.append(engine_grid[k][i+1])
                if k != 0:
                    neighbors.append(engine_grid[k-1][i])
                if k != area_height_num-1:
                    neighbors.append(engine_grid[k+1][i])
                engine.set_neighbors.remote(neighbors)  
                self.engines.append(engine)
                print("Engine: {}, Add Neighbors: {}".format(engine, [nei for nei in neighbors]))
            

    def run(self):
        self.prepare()
        num = 5
        total_time = 0
        for i in range(num):
            start = time.time()
            #results = []
            step_num = self.scenario.step_num
            #print("Engine Num: {}".format(len(self.engines)))
            for i in range(step_num):
                wip_engines = [engine.step.remote() for engine in self.engines]
                ray.get(wip_engines)
                wip_engines = [engine.poststep.remote() for engine in self.engines]
                ray.get(wip_engines)
                elapsed_time = time.time() - start
                #print("Finished All Engines Step {},  Elapsed: {:.3f}[sec]".format(i, elapsed_time))
                #results.append({"timestamp": i, "data": [{"agents": info["agents"], "area": info["area"]} for info in infos]})
            elapsed_time = time.time() - start
            total_time += elapsed_time
            print("iter: {}, time: {}".format(i, elapsed_time))
        elapsed_time = total_time/num
        print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
        #self.plot(results, self.env, colored_by="AGENT")
            

    def plot(self, results, env, colored_by="AGENT"):
        # colored_by: "AREA" or "AGENT", default is "AGENT"
        # results: [{"timestamp": 0, "data": [{"area": Area, "agents": [Agent]}, ... ] }, {"timestamp": 1, "data": [{"area": Area, "agents": [Agent]}, ...]} ...]
        if len(results) == 0:
            print("Warning: results is empty")
            return

        def get_random_color():
            return "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])

        if colored_by == "AGENT":
            max_type_num = 10
            colors = [get_random_color() for i in range(max_type_num)]
            color_map = {}
        else:
            area_num = len(results[0]["data"])
            colors = [get_random_color() for i in range(area_num)]
        
        def _update_colored_area(frame):
            plt.cla()
            index = frame
            data = results[index]["data"]
            plt.xlim(env.area.start_x,env.area.end_x)
            plt.ylim(env.area.start_y,env.area.end_y)
            for i, d in enumerate(data):
                area = d["area"]
                plt.vlines(x=area.start_x, ymin=area.start_y, ymax=area.end_y)
                plt.vlines(x=area.end_x, ymin=area.start_y, ymax=area.end_y)
                plt.hlines(y=area.start_y, xmin=area.start_x, xmax=area.end_x)
                plt.hlines(y=area.end_y, xmin=area.start_x, xmax=area.end_x)
                agents = d["agents"]
                x, y = [], []
                for agent in agents:
                    x.append(agent.position.x)
                    y.append(agent.position.y)
                plt.scatter(x, y, c=colors[i], label='Area{}'.format(area.id))
            plt.legend(loc='lower left')
            

        def _update_colored_agent(frame):
            plt.cla()
            index = frame
            data = results[index]["data"]
            plt.xlim(env.area.start_x,env.area.end_x)
            plt.ylim(env.area.start_y,env.area.end_y)
            agents_type_map = {}
            for i, d in enumerate(data):
                area = d["area"]
                plt.vlines(x=area.start_x, ymin=area.start_y, ymax=area.end_y)
                plt.vlines(x=area.end_x, ymin=area.start_y, ymax=area.end_y)
                plt.hlines(y=area.start_y, xmin=area.start_x, xmax=area.end_x)
                plt.hlines(y=area.end_y, xmin=area.start_x, xmax=area.end_x)
                agents = d["agents"]
                for agent in agents:
                    if agent.type not in agents_type_map.keys():
                        agents_type_map[agent.type] = {"x": [], "y": [], "color": "red"}
                    if agent.type not in color_map.keys():
                        color_map[agent.type] = get_random_color()
                    agents_type_map[agent.type]["x"].append(agent.position.x)
                    agents_type_map[agent.type]["y"].append(agent.position.y)
                    agents_type_map[agent.type]["color"] = agent.color

            index = 0
            for k, v in agents_type_map.items():
                plt.scatter(v["x"], v["y"], c=v["color"], label=k)
                index += 1
            plt.legend(loc="lower left")

        fig = plt.figure(figsize=(10, 6))

        params = {
            'fig': fig,
            'func': _update_colored_agent if colored_by=="AGENT" else _update_colored_area,  # update function
            'fargs': (),  # args of update function
            'interval': 100,  # update interval
            'frames': np.arange(0, len(results), 1),  # frame index
            'repeat': True, 
        }
        anime = animation.FuncAnimation(**params)

        dir_path = './results/{}'.format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(dir_path, exist_ok=True)
        anime.save("{}/result.gif".format(dir_path),writer='imagemagick')
        plt.show()


