import datetime
import os
import ndjson
import glob
from matplotlib import pyplot as plt
import random
from matplotlib import animation
import numpy as np

class Visualizer:
    def __init__(self, log_dir):
        self.log_dir = log_dir

    def plot(self):
        print("plot vis")
        scalar_files = glob.glob("{}/*.scalar.ndjson".format(self.log_dir))
        agents_files = glob.glob("{}/agents.ndjson".format(self.log_dir))
        #print(scalar_files, agents_files)
        axs_num = len(scalar_files) + len(agents_files)
        fig = plt.figure(figsize=(4*axs_num,4))
        axs = {"agents": [], "scalar": []}
        for agents_file in agents_files:
            data = self.load_json(agents_file)
            axs["agents"].append(fig.add_subplot(1, axs_num, 1))
            break
        for i, scalar_file in enumerate(scalar_files):
            data = self.load_json(scalar_file)
            print(data)
            axs["scalar"].append(fig.add_subplot(1, axs_num, i+2))


        theta = np.linspace(0, 4*np.pi, 128)

        def update(f):
            for ax in axs:
                ax.cla() # ax をクリア
                ax.grid()
            
            axs[0].plot(np.sin(theta), np.cos(theta), c="gray")
            axs[0].plot(np.sin(f), np.cos(f), "o", c="blue")
            axs[0].plot(0, np.cos(f), "o", c="blue")
            axs[0].plot([0, np.sin(f)], [np.cos(f), np.cos(f)], c="blue")

            axs[1].plot(np.sin(theta), np.cos(theta), c="gray")
            axs[1].plot(np.sin(f), np.cos(f), "o", c="blue")
            axs[1].plot(0, np.cos(f), "o", c="blue")
            axs[1].plot([0, np.sin(f)], [np.cos(f), np.cos(f)], c="blue")
        

        anim = animation.FuncAnimation(fig, update, frames=np.pi*np.arange(0,2,0.1), interval=200)

        plt.show()
        

    def load_json(self, file_name: str):
        with open(file_name) as f:
            data = ndjson.load(f)
        return data

    def plot2(self, results, env, colored_by="AGENT"):
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
