import datetime
import os
from filelock import FileLock
import json
import ndjson

class SummaryWriter:
    def __init__(self, log_dir=None):
        self.log_dir = './results/{}'.format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")) if log_dir == None else log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.scalar_data = {}
        self.agents_data = []
        

    def write(self, file_name: str, dict: dict):
        file_path = "{}/{}".format(self.log_dir, file_name)
        #with FileLock("{}.lock".format(file_path)):
        with open(file_path,"a") as f:
            writer = ndjson.writer(f)
            writer.writerow(dict)
            #f.write(text)

    def add_scalar(self, tag: str, scalar_value: float, global_step: float):
        '''if tag in self.scalar_data:
            self.scalar_data[tag].append([scalar_value, global_step])
        else:
            self.scalar_data[tag] = [[scalar_value, global_step]]'''
        self.write("{}.scalar.ndjson".format(tag), {"step": global_step, "value": scalar_value})

    def add_agents(self, agents, global_step: float):
        def default_method(item):
            if isinstance(item, object) and hasattr(item, '__dict__'):
                return item.__dict__
            else:
                raise TypeError
        json_agents = []
        for agent in agents:
            json_agents.append(json.loads(json.dumps(agent, default=default_method)))
        self.write("agents.ndjson", {"step": global_step, "agents": json_agents})
        #self.agents_data.append(json.dumps({"agents": json_agents, "step": global_step}))
    