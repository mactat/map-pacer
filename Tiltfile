# Agent
k8s_yaml('./agent/kubernetes.yaml')
k8s_resource('agent-statefullset')
docker_build('mactat/map-pacer-agent', './agent')

# Backend
k8s_yaml('./backend/kubernetes.yaml')
k8s_resource('backend-deployment', port_forwards=8022)
docker_build('mactat/map-pacer-backend', './backend')

# Frontend
k8s_yaml('./frontend/kubernetes.yaml')
k8s_resource('frontend-deployment', port_forwards=8023)
docker_build('mactat/map-pacer-frontend', './frontend')

# Map-service
k8s_yaml('./map-service/kubernetes.yaml')
k8s_resource('map-service-deployment', port_forwards=8024)
docker_build('mactat/map-pacer-map-service', './map-service')

# Cloud-agent
k8s_yaml('./cloud-agent/kubernetes.yaml')
k8s_resource('cloud-agent-deployment', port_forwards=8025)
docker_build('mactat/map-pacer-cloud-agent', './cloud-agent')

# Redis
# load('ext://helm_resource', 'helm_resource', 'helm_repo')
# helm_repo('bitnami', 'https://charts.bitnami.com/bitnami')
# helm_resource('redis', 'bitnami/redis')

# Broker
k8s_yaml('./broker/kubernetes.yaml')
k8s_resource('broker-deployment')
k8s_yaml('./broker/service.yaml')
k8s_kind('broker-service')
