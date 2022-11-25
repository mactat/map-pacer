# Broker
k8s_yaml('./broker/kubernetes.yaml')
k8s_resource('broker', labels=["core-module"])

# Cloud-Broker
k8s_yaml(helm("cloud-broker", name="cloud-broker", values="./cloud-broker/values.yaml"))
k8s_resource('cloud-broker', labels=["core-module-cloud"])

# Agent
objects = read_yaml_stream('./agent/kubernetes.yaml')
objects[0]['spec']['template']['spec']['containers'][0]['env'][3]['value'] = 'cloud-broker'
objects[0]['spec']['template']['spec']['containers'][0]['env'][4]['value'] = '9001'
k8s_yaml(encode_yaml_stream(objects))
k8s_resource('agent',  labels=["core-module"], resource_deps=['broker', 'cloud-broker'])
docker_build('mactat/map-pacer-agent', './', dockerfile='./agent/Dockerfile')

# Database
k8s_yaml('./database/kubernetes.yaml')
k8s_resource('database', labels=["visualization-module"])

# Backend
k8s_yaml('./backend/kubernetes.yaml')
k8s_resource('backend', port_forwards=8022, labels=["visualization-module"], resource_deps=['broker', 'cloud-broker'])
docker_build('mactat/map-pacer-backend', './', dockerfile='./backend/Dockerfile')

# Frontend
# Change backend url in frontend
objects = read_yaml_stream('./frontend/kubernetes.yaml')
objects[0]['spec']['template']['spec']['containers'][0]['env'][0]['value'] = 'http://localhost:8022/backend'
k8s_yaml(encode_yaml_stream(objects))
k8s_resource('frontend', port_forwards=8023, labels=["visualization-module"], resource_deps=['backend'])
docker_build('mactat/map-pacer-frontend', './frontend')

# performance-test
k8s_yaml('./performance-test/kubernetes.yaml')
k8s_resource('performance-test' , labels=["test-module"], resource_deps=['backend'])
docker_build('mactat/map-pacer-performance-test', './performance-test')

# button
load('ext://uibutton', 'cmd_button')
cmd_button('performance-test:start test',
        argv=['make', 'performance', "SYSTEM_ID=home_system"],
        resource='performance-test',
        icon_name='rocket_launch',
        text='start test',
)

# Map-service
objects = read_yaml_stream('./map-service/kubernetes.yaml')
objects[0]['spec']['template']['spec']['containers'][0]['env'][3]['value'] = 'cloud-broker'
objects[0]['spec']['template']['spec']['containers'][0]['env'][4]['value'] = '9001'
k8s_yaml(encode_yaml_stream(objects))
k8s_resource('map-service',  labels=["core-module"], resource_deps=['broker', 'cloud-broker'])
docker_build('mactat/map-pacer-map-service', './', dockerfile='./map-service/Dockerfile')

# Cloud-agent
k8s_yaml('./cloud-agent/kubernetes.yaml')
k8s_resource('cloud-agent', labels=["core-module"], resource_deps=['broker', 'cloud-broker'])
docker_build('mactat/map-pacer-cloud-agent', './', dockerfile='./cloud-agent/Dockerfile')

## FOREIGN SYSTEM TEST
# System-2(foreign)
k8s_yaml('./agent/kubernetes_foreign.yaml')
k8s_resource('agent-foreign',  labels=["foreign-system"], resource_deps=['broker', 'cloud-broker'])

# Map-service
k8s_yaml('./map-service/kubernetes _foreign.yaml')
k8s_resource('map-service-foreign',  labels=["foreign-system"], resource_deps=['broker', 'cloud-broker'])
# load('ext://helm_resource', 'helm_resource', 'helm_repo')
# helm_repo('bitnami', 'https://charts.bitnami.com/bitnami')
# helm_resource('redis', 'bitnami/redis')
