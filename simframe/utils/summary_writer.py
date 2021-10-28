import datetime
import os
class FileWriter:
    def __init__(self, log_dir=None):
        self.log_dir = '../results/{}'.format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")) if log_dir == None else log_dir
        self.scalar_data = {}
        self.agents_data = []

class SummaryWriter:
    def __init__(self, log_dir=""):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.scalar_data = {}
        self.agents_data = []
        
    @property
    def file_writer(self):
        return self.file_writer

    def write(self, data):
        file_path = "{}/test.txt".format(self.log_dir)
        with open(file_path, mode='a') as f:
            f.write('\n'.join(data))

    def add_scalar(self, tag: str, scalar_value: float, global_step: float):
        if tag in self.scalar_data:
            self.scalar_data[tag].append([scalar_value, global_step])
        else:
            self.scalar_data[tag] = [[scalar_value, global_step]]
        self.write(scalar_value)

    def add_agents(self, agents, global_step: float):
        self.agents_data.append({"agents": agents, "step": global_step})
    

if __name__ == "__main__":
    sw = SummaryWriter()
    sw.add_scalar("test", "a", 1)
    sw.add_scalar("test", "b", 2)
    sw.add_scalar("test", "c", 3)