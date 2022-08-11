# MAP-PACER - multiple agents path planing algorithms using cloud and edge resources

## Description

Comparison of path planning algorithms for multiple robots based on edge-cloud collaborative computing, cloud computing, and local computing

## Initial idea
![Initial idea](/docs/diagrams/initial.png)

## Services architecture
![Services architecture](/docs/diagrams/services.png)

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

## Cloud deployment
```bash
to be finished
```

## Algorithms
```bash
to be finished
```