# Deploy on Kubernetes

# How to Start
Reference: https://docs.ray.io/en/latest/cluster/kubernetes.html

## 0. Build Program
```
cd simframe_ray
bash docker_build.sh
```

## 1. Prepare Ray Cluster 
```
cd simframe_ray/deploy/charts
helm -n ray install example-cluster --create-namespace ./ray
kubectl -n ray port-forward service/example-cluster-ray-head 10001:10001
```

## 2. Run Program
```
cd simframe_ray
kubectl -n ray create -f  deploy/run.yaml
```

## 3. Check Log
```
$ kubectl -n ray get pods
NAME                                    READY   STATUS    RESTARTS   AGE
example-cluster-ray-head-type-5926k     1/1     Running   0          21m
example-cluster-ray-worker-type-8gbwx   1/1     Running   0          21m
example-cluster-ray-worker-type-l6cvx   1/1     Running   0          21m
ray-test-job-dl9fv                      1/1     Running   0          3s

# Fetch the logs. You should see repeated output for 10 iterations and then
# 'Success!'
$ kubectl -n ray logs ray-test-job-dl9fv
```

## 4. Cleanup Program
```
kubectl -n ray delete job ray-test-job
```

## 5. Cleanup Cluster
```
# First, delete the RayCluster custom resource.
$ kubectl -n ray delete raycluster example-cluster
raycluster.cluster.ray.io "example-cluster" deleted

# Delete the Ray release.
$ helm -n ray uninstall example-cluster
release "example-cluster" uninstalled

# Optionally, delete the namespace created for our Ray release.
$ kubectl delete namespace ray
namespace "ray" deleted
```


## Note
If the program run on head node, shoud be ray.init(address="auto").