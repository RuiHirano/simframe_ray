from abc import ABCMeta, abstractmethod
import random
from typing import List
from .engine import Engine
from .agent import Agent, Position
from .area import Area
import ray
from matplotlib import pyplot as plt
from matplotlib import animation
import numpy as np

class Master:
    def __init__(self, config):
        self.config = config
        self.engines: List[Engine] = []

    def prepare(self):
        area_num = 3
        for i in range(area_num):
            # area
            area = Area(
                start_x=i*100,
                end_x=(i+1)*100,
                start_y=0,
                end_y=100
            )
            # agents
            agents = []
            agent_num = 100
            for k in range(agent_num):
                position = Position(
                    x=area.start_x + (area.end_x-area.start_x) * random.random(),
                    y=area.start_y + (area.end_y-area.start_y) * random.random()
                )
                agents.append(Agent("{}-{}".format(i, k), position))
            # engine
            neighbors = self.engines
            self.engines.append(Engine.remote(str(i), neighbors, area, agents))

    def run(self):
        results = []
        step_num = 10
        for i in range(step_num):
            wip_engines = [engine.prestep.remote() for engine in self.engines]
            ray.get(wip_engines)
            wip_engines = [engine.step.remote() for engine in self.engines]
            infos = ray.get(wip_engines)
            wip_engines = [engine.poststep.remote() for engine in self.engines]
            ray.get(wip_engines)
            print(infos)
            print("Finished All Engines Step {}".format(i))
            results.append({"timestamp": i, "agents": [agent for info in infos for agent in info["agents"]]})
        print(results)
        self.plot(results)
            

    def plot(self, results):
        # results: [{"timestamp": 0, "agents": []}, {"timestamp": 0, "agents": []} ...]

        def _update(frame):
            plt.cla()
            index = frame
            agents = results[index]["agents"]
            x, y = [], []
            for agent in agents:
                x.append(agent.position.x)
                y.append(agent.position.y)
            # 折れ線グラフを再描画する
            plt.xlim(0,300)
            plt.ylim(0,100)
            plt.vlines(x=100, ymin=0, ymax=100)
            plt.vlines(x=200, ymin=0, ymax=100)
            plt.scatter(x, y)

        # 描画領域
        fig = plt.figure(figsize=(10, 6))
        # 描画するデータ (最初は空っぽ)

        params = {
            'fig': fig,
            'func': _update,  # グラフを更新する関数
            'fargs': (),  # 関数の引数 (フレーム番号を除く)
            'interval': 1000,  # 更新間隔 (ミリ秒)
            'frames': np.arange(0, len(results), 1),  # フレーム番号を生成するイテレータ
            'repeat': True,  # 繰り返さない
        }
        anime = animation.FuncAnimation(**params)

        # グラフを表示する
        plt.show()


