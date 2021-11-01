import datetime
import os
import ndjson
import glob
from matplotlib import pyplot as plt
import random
from matplotlib import animation
import numpy as np
import copy

class Visualizer:
    def __init__(self, log_dir):
        self.log_dir = log_dir

    def plot(self):
        print("plot vis")
        scalar_files = glob.glob("{}/*.scalar.ndjson".format(self.log_dir))
        agents_files = glob.glob("{}/*.agents.ndjson".format(self.log_dir))
        #print(scalar_files, agents_files)
        axs_num = len(scalar_files) + len(agents_files)
        fig = plt.figure(figsize=(4*axs_num,4))
        plot_data = {"agents": [], "scalar": []}
        step_num = 0
        for agents_file in agents_files:
            data = self.load_json(agents_file)
            agents_data, step_num = self.modified_agents_data(data)
            #print(agents_data)
            plot_data["agents"].append({"ax": fig.add_subplot(1, axs_num, 1), "data": agents_data})
            
        for i, scalar_file in enumerate(scalar_files):
            data = self.load_json(scalar_file)
            scalar_data, step_num = self.modified_scalar_data(data)
            plot_data["scalar"].append({"ax": fig.add_subplot(1, axs_num, i+1+len(agents_files)), "data": scalar_data})


        def get_random_color():
            return "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
        color_map = {}


        agents_data_list = plot_data["agents"]
        scalar_data_list = plot_data["scalar"]
        
        def update(f):
            index = f
            for agents_data in agents_data_list:
                ax = agents_data["ax"]
                one_step_data = agents_data["data"][index]
                one_step_agents = one_step_data["agents"]
                #print(data, index)
                ax.cla() # ax をクリア
                ax.set_xlim(0, 300)
                ax.set_ylim(0, 300)
                agents_type_map = {}
                for agent in one_step_agents:
                    if agent["type"] not in agents_type_map.keys():
                        agents_type_map[agent["type"]] = {"x": [], "y": []}
                    if agent["type"] not in color_map.keys():
                        color_map[agent["type"]] = get_random_color()
                    agents_type_map[agent["type"]]["x"].append(agent["position"]["x"])
                    agents_type_map[agent["type"]]["y"].append(agent["position"]["y"])
                for k, v in agents_type_map.items():
                    ax.scatter(v["x"], v["y"], c=color_map[k], label=k)
                #ax.legend(loc="lower left")

            for scalar_data in scalar_data_list:
                ax = scalar_data["ax"]
                one_step_data = scalar_data["data"][index]
                values = one_step_data["values"]
                
                ax.cla() # ax をクリア
                ax.grid()
                ax.set_xlim(0, step_num)
                ax.set_ylim(0, max(values))
                ax.plot(np.arange(0, index+1, 1), values, c="red", label="value")
        
        anime = animation.FuncAnimation(fig, update, frames=np.arange(0, step_num, 1), interval=200)
        anime.save("{}/result.gif".format(self.log_dir),writer='imagemagick')
        plt.show()
    
    def modified_agents_data(self, data):
        # conbine data by step
        target_step = -1
        agents = []
        result = []
        for d in data:
            step = d["step"]
            if target_step == -1:
                target_step == step
            if step != target_step:
                result.append({"step": target_step, "agents": agents})
                agents = []
                target_step = step
            agents.extend(d["agents"])
        return result, len(result)

    def modified_scalar_data(self, data):
        # conbine data by step
        target_step = -1
        result = []
        values = []
        value = 0
        for d in data:
            step = d["step"]
            if target_step == -1:
                target_step = step
            if step != target_step:
                values.append(value)
                result.append({"step": target_step, "values": copy.deepcopy(values)})
                value = 0
                target_step = step
            value += d["value"]
        return result, len(result)

    def load_json(self, file_name: str):
        with open(file_name) as f:
            data = ndjson.load(f)
        return data
