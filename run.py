from lib.master import Master
import ray 
import os
import time

RAY_CLUSTER_HOST = os.environ.get('RAY_CLUSTER_HOST')

def wait_for_nodes(expected):
    # Wait for all nodes to join the cluster.
    while True:
        resources = ray.cluster_resources()
        node_keys = [key for key in resources if "node" in key]
        num_nodes = sum(resources[node_key] for node_key in node_keys)
        if num_nodes < expected:
            print("{} nodes have joined so far, waiting for {} more.".format(
                num_nodes, expected - num_nodes))
            time.sleep(1)
        else:
            break

if __name__ == "__main__":
    if RAY_CLUSTER_HOST:
        ray.init(address=RAY_CLUSTER_HOST)
        wait_for_nodes(3)
    else:
        ray.init()
    print("Head Address: ", RAY_CLUSTER_HOST)
    master = Master("")
    master.prepare()
    master.run()