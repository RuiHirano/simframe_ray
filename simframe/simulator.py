from abc import ABCMeta, abstractmethod
import random
from typing import List
from .engine import Engine
from .agent import Agent, Position
from .area import Area
from .environment import Environment
from .model import Model
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
    def __init__(self, model: Model):
        self.model = model
        self.env = model.env
        self.engines: List[Engine] = []

    def prepare(self):
        area_num = 3 # default is 3 cpu process, divide 3 areas by x axis
        engines = []
        for i in range(area_num):
            # area
            area = Area(
                id=str(i),
                start_x=self.env.area.start_x + (self.env.area.end_x-self.env.area.start_x)*(i/area_num),
                end_x=self.env.area.start_x + (self.env.area.end_x-self.env.area.start_x)*((i+1)/area_num),
                start_y=self.env.area.start_y,
                end_y=self.env.area.end_y
            )
            # agents
            agents = [agent for agent in self.model.agents if area.is_in(agent)]

            # engine
            engines.append(Engine.remote(str(i), area, agents))

        for i, engine in enumerate(engines):
            # TODO: create adaptive area divider
            if i == 0 or i ==2:
                neighbors = [engines[1]]
            if i == 1:
                neighbors = [engines[0], engines[2]] 
            engine.set_neighbors.remote(neighbors)  
            self.engines.append(engine)

    def run(self):
        self.prepare()
        start = time.time()
        results = []
        step_num = self.model.step_num
        for i in range(step_num):
            wip_engines = [engine.step.remote() for engine in self.engines]
            infos = ray.get(wip_engines)
            wip_engines = [engine.poststep.remote() for engine in self.engines]
            ray.get(wip_engines)
            elapsed_time = time.time() - start
            print("Finished All Engines Step {},  Elapsed: {:.3f}[sec]".format(i, elapsed_time))
            results.append({"timestamp": i, "data": [{"agents": info["agents"], "area": info["area"]} for info in infos]})
        elapsed_time = time.time() - start
        print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
        self.plot(results, self.env, colored_by="AGENT")
            

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
                        agents_type_map[agent.type] = {"x": [], "y": []}
                    if agent.type not in color_map.keys():
                        color_map[agent.type] = get_random_color()
                    agents_type_map[agent.type]["x"].append(agent.position.x)
                    agents_type_map[agent.type]["y"].append(agent.position.y)

            index = 0
            for k, v in agents_type_map.items():
                plt.scatter(v["x"], v["y"], c=color_map[k], label=k)
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


