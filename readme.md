![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)
[![CI/CD](https://github.com/mactat/map-pacer/actions/workflows/ci_cd.yml/badge.svg)](https://github.com/mactat/map-pacer/actions/workflows/ci_cd.yml)
[![Build Status](https://dev.azure.com/s202609/Hello-world/_apis/build/status/Build%20and%20Push%20agent%20image?branchName=master)](https://dev.azure.com/s202609/Hello-world/_build/latest?definitionId=10&branchName=master)
[![thesis-release](https://github.com/mactat/map-pacer/actions/workflows/thesis-release.yml/badge.svg)](https://github.com/mactat/map-pacer/actions/workflows/thesis-release.yml)

![Initial idea](./frontend/static/favicon.ico)
# MAP-PACER - multiple agents path planing algorithms using cloud and edge resources

## Description

Comparison of path planning algorithms for multiple robots based on edge-cloud collaborative computing, cloud computing, and local computing

## Initial idea
![Initial idea](./docs/thesis/pictures/initial.png)

## Services architecture
![Services architecture](./docs/thesis/pictures/services.png)

## Local testing
1) Install vagrant and virtualbox
2) Use pre configured [machine](https://github.com/mactat/dev-vm)
3) Start ssh session to machine: 
```
ssh dev-vm@localhost -p 2222
```
4) Clone repo
5) Use tilt for development and testing
```bash
tilt up
```

This includes live cde changes and automatic deployment to local kubernetes cluster managed by `kind`.

## General development
```bash
For spinning dev-env, tilt, kind and ctlptl has to be configured.
For cloud development add '.env' file with:
AZURE_SUBSCRIPTION_ID, AZURE_GROUP_NAME, AZURE_CLUSTER_NAME, DOCKER_TOKEN, DOCKER_USERNAME

Usage:
	make dev                      run dev cluster and tilt
	make clean                    stop local cluster and tilt
	make cloud-login              login to azure and setup kubectl
	make cloud-up                 start kubernetes cluster in azure
	make cloud-down               stop kubernetes cluster in azure
	make cloud-deploy             deploy to kubernetes cluster in azure
	make cloud-build	      build and push docker images
	make plots RESULTS=<res_file> creates plots, provide <RESULTS> file
	make ping-plots		      test RTT time to cloud
	make pdf		      compile thesis to pdf
	make local-observability      deploy prometheus and graphana
	make performance 	      make performance test against
	  SYSTEM_ID=<system_id>       selected system
	  FLAGS=<--json > file.json>
	
```

## Algorithms
```bash
# Basic A*, Dijkstra, BFS
# Advanced CA*
```
### CA* sequence diagram
![CA* sequence diagram](./docs/thesis/pictures/ca_start_sequence.png)

## Map
Maps are set to be grid based and are represented as 2D array of integers. Each integer represents a cell in the grid. Those grids are transformed into graphs and then used for path planning.

Planning can be based on 2D maps(representing just space) or 3D maps(representing both time and space).

### Principle of graph creation for 2D map:
![2D map](./docs/thesis/pictures/map_2d.png)

### Principle of graph creation for 3D map:
![3D map](./docs/thesis/pictures/map_3d.png)

## Logic for path planning
![Example](./docs/thesis/pictures/example_planning.png)

### Example of planned path:
![Solved map](./docs/thesis/pictures/single_path_maze.png)

### Example of solved map for multiple agents(development vis):
![Solved map](./docs/thesis/pictures/example_planning.gif)

![Solved map](./docs/thesis/pictures/multi_agent_dev_1.gif)

## Observability
Observability in this project is based on prometheus and grafana. Grafana is used for visualizing metrics and prometheus is used for collecting them.
To deply grafana and prometheus locally use:
```bash
make local-observability
```

It can be used in multiple setups:
![Observability](./docs/thesis/pictures/observability.png)

Example of grafana dashboard:
![Grafana dashboard](./docs/thesis/pictures/grafana.png)

## Multi tenancy
By design this is multi tenant system, tenants can share resources like broker and upstream computation to the cloud:
![Multi tenancy](./docs/thesis/pictures/multi_tenant_simple.png)

# Results
## Path finding time
![Path finding time](./docs/thesis/pictures/on_prem_test_time.png)

## Path finding time(log)
![Path finding time log](./docs/thesis/pictures/on_prem_test_time_log.png)

## Other stats
![other stats](./docs/thesis/pictures/on_prem_test_subplot.png)

## Agent - Cloud - RTT
![RTT](./docs/thesis/pictures/ping.png)