# Broker
k8s_yaml('./broker/kubernetes.yaml')
k8s_resource('broker', labels=["core-module"])

# Cloud-Broker
k8s_yaml('./cloud-broker/kubernetes.yaml')
k8s_resource('cloud-broker', labels=["core-module"])

# Agent
k8s_yaml('./agent/kubernetes.yaml')
k8s_resource('agent',  labels=["core-module"], resource_deps=['broker', 'cloud-broker'])
docker_build('mactat/map-pacer-agent', './', dockerfile='./agent/Dockerfile')

# Backend
k8s_yaml('./backend/kubernetes.yaml')
k8s_resource('backend', port_forwards=8022, labels=["visualization-module"], resource_deps=['broker', 'cloud-broker'])
docker_build('mactat/map-pacer-backend', './backend')

# Frontend

# Change backend url in frontend
objects = read_yaml_stream('./frontend/kubernetes.yaml')
objects[0]['spec']['template']['spec']['containers'][0]['env'][0]['value'] = 'http://localhost:8022/backend'
k8s_yaml(encode_yaml_stream(objects))


# k8s_yaml('./frontend/kubernetes.yaml')
k8s_resource('frontend', port_forwards=8023, labels=["visualization-module"], resource_deps=['backend'])
docker_build('mactat/map-pacer-frontend', './frontend')

# Map-service
k8s_yaml('./map-service/kubernetes.yaml')
k8s_resource('map-service',  labels=["core-module"], resource_deps=['broker', 'cloud-broker'])
docker_build('mactat/map-pacer-map-service', './', dockerfile='./map-service/Dockerfile')

# Cloud-agent
k8s_yaml('./cloud-agent/kubernetes.yaml')
k8s_resource('cloud-agent', labels=["core-module"], resource_deps=['broker', 'cloud-broker'])
docker_build('mactat/map-pacer-cloud-agent', './', dockerfile='./cloud-agent/Dockerfile')

# Redis
# load('ext://helm_resource', 'helm_resource', 'helm_repo')
# helm_repo('bitnami', 'https://charts.bitnami.com/bitnami')
# helm_resource('redis', 'bitnami/redis')