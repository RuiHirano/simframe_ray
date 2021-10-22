from abc import ABCMeta, abstractmethod
import random
from typing import List
from lib.engine import Engine
from lib.agent import Agent, Position
from lib.area import Area
from lib.environment import Environment
import ray
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np
import os
import datetime

import multiprocessing
print("cpu num: ", multiprocessing.cpu_count())

class Master:
    def __init__(self, env: Environment):
        self.env = env
        self.engines: List[Engine] = []

    def prepare(self):
        area_num = 3 # default is 3 cpu process
        for i in range(area_num):
            # area
            area = Area(
                start_x=self.env.area.start_x + (self.env.area.end_x-self.env.area.start_x)*(i/area_num),
                end_x=self.env.area.start_x + (self.env.area.end_x-self.env.area.start_x)*((i+1)/area_num),
                start_y=self.env.area.start_y,
                end_y=self.env.area.end_y
            )
            # agents
            agents = [agent for agent in self.env.agents if area.is_in(agent)]

            # engine
            neighbors = self.engines
            self.engines.append(Engine.remote(str(i), neighbors, area, agents))

    def run(self):
        results = []
        step_num = self.env.step_num
        for i in range(step_num):
            wip_engines = [engine.prestep.remote() for engine in self.engines]
            ray.get(wip_engines)
            wip_engines = [engine.step.remote() for engine in self.engines]
            infos = ray.get(wip_engines)
            wip_engines = [engine.poststep.remote() for engine in self.engines]
            ray.get(wip_engines)
            print("Finished All Engines Step {}".format(i))
            results.append({"timestamp": i, "data": [{"agents": info["agents"], "area": info["area"]} for info in infos]})
        self.plot(results, self.env)
            

    def plot(self, results, env):
        # results: [{"timestamp": 0, "data": [{"area": Area, "agents": [Agent]}, ... ] }, {"timestamp": 1, "data": [{"area": Area, "agents": [Agent]}, ...]} ...]
        if len(results) == 0:
            print("Warning: results is empty")
            return
        def get_random_color():
            return "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
        print(len(results[0]["data"]))
        colors = [get_random_color() for i in range(len(results[0]["data"]))]
        
        def _update(frame):
            plt.cla()
            index = frame
            data = results[index]["data"]
            plt.xlim(env.area.start_x,env.area.end_x)
            plt.ylim(env.area.start_y,env.area.end_y)
            for i, d in enumerate(data):
                agents = d["agents"]
                area = d["area"]
                x, y = [], []
                for agent in agents:
                    x.append(agent.position.x)
                    y.append(agent.position.y)
                plt.vlines(x=area.start_x, ymin=area.start_y, ymax=area.end_y)
                plt.vlines(x=area.end_x, ymin=area.start_y, ymax=area.end_y)
                plt.hlines(y=area.start_y, xmin=area.start_x, xmax=area.end_x)
                plt.hlines(y=area.end_y, xmin=area.start_x, xmax=area.end_x)
                plt.scatter(x, y, c=colors[i])

        fig = plt.figure(figsize=(10, 6))

        params = {
            'fig': fig,
            'func': _update,  # update function
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


