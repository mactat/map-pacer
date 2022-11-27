# Define required macros here
SHELL = /bin/bash
CUR_DIR="$(shell pwd)"
PERFORMANCE_POD="$(shell kubectl get pod -l app=performance-test -o jsonpath='{.items[0].metadata.name}')"
include .env
export

define PROJECT_HELP_MSG
Makefile for map-pacer project
For spinning dev-env, tilt, kind and ctlptl has to be configured.
For cloud development add '.env' file with:
AZURE_SUBSCRIPTION_ID, AZURE_GROUP_NAME, CLUSTER_NAME, DOCKER_TOKEN, DOCKER_USERNAME

Usage:
	make dev                    run dev cluster and tilt
	make clean                  stop local cluster and tilt
	make cloud-login            login to azure and setup kubectl
	make cloud-up               start kubernetes cluster in azure
	make cloud-down             stop kubernetes cluster in azure
	make cloud-deploy           deploy to kubernetes cluster in azure
	make cloud-build			build and push docker images
endef

export PROJECT_HELP_MSG

help:
	echo "$$PROJECT_HELP_MSG" | less


.PHONY: dev
dev:
	kubectl config use-context kind-kind
	tilt up
.PHONY: performance
performance:
	kubectl exec $(PERFORMANCE_POD) -- python3 /app/test.py --system_id=$(SYSTEM_ID) $(FLAGS)

.PHONY: plots
plots:
	cd ./tools && export RESULTS=$(RESULTS) && docker compose run --rm plots      
.PHONY: local-observability
local-observability:
	kubectl config use-context kind-kind
	kubectl create -f ./observability/kube-prometheus/manifests/setup
	kubectl get ns monitoring
	kubectl create -f ./observability/kube-prometheus/manifests/
	kubectl get pods -n monitoring
	kubectl --namespace monitoring port-forward svc/prometheus-k8s 9090

.PHONY: cloud-login
cloud-login:
	# Login to the cloud
	az login --use-device-code

	# Set connection details
	az account set --subscription $(AZURE_SUBSCRIPTION_ID)
	az aks get-credentials --resource-group $(AZURE_GROUP_NAME) --name $(CLUSTER_NAME)

	# Check the context
	echo "Current context:"
	kubectl config current-context
	kubectl config set-context --current --namespace=$(K8S_NAMESPACE)

# Cloud create
# az login --use-device-code
# az account set --subscription $(AZURE_SUBSCRIPTION_ID)
# az group create --name $(AZURE_GROUP_NAME) --location northeurope
# az aks create -g $(AZURE_GROUP_NAME) -n $(CLUSTER_NAME) --node-count 4 --node-vm-size Standard_A8_v2
# deploy application gateway

.PHONY: cloud-up
cloud-up:
	# Start the cluster
	az aks start --name $(CLUSTER_NAME) --resource-group $(AZURE_GROUP_NAME)

.PHONY: cloud-down
cloud-down:
	# Stop the cluster
	az aks stop --name $(CLUSTER_NAME) --resource-group $(AZURE_GROUP_NAME)

CLOUD_SERVICES= cloud-agent cloud-broker backend frontend
.PHONY: cloud-deploy
cloud-deploy:
	echo "deploying to cluster"
	kubectl config use-context $(CLUSTER_NAME)
	kubectl config set-context --current --namespace=$(K8S_NAMESPACE)
	@for service in $(CLOUD_SERVICES); do \
        kubectl apply -f "$$service/kubernetes.yaml"; \
    done

	# to be change in a real cluster
	# kubectl --namespace monitoring port-forward svc/prometheus-k8s 9090 &
	# kubectl --namespace monitoring port-forward svc/grafana 3000 &

.PHONY: cloud-deploy-broker
cloud-deploy-broker:
	echo "deploying broker to cluster"
	kubectl config use-context $(CLUSTER_NAME)
	kubectl config set-context --current --namespace=$(K8S_NAMESPACE)
	helm repo add hivemq https://hivemq.github.io/helm-charts
	helm upgrade --install -f ./cloud-broker/kubernetes.yaml cloud-broker hivemq/hivemq-operator

.PHONY: cloud-build
cloud-build:
	docker login -u $(DOCKER_USERNAME) -p $(DOCKER_TOKEN)
	echo "Building images"
	docker build -t $(DOCKER_USERNAME)/map-pacer-cloud-agent:latest -f ./cloud-agent/Dockerfile .
	docker build -t $(DOCKER_USERNAME)/map-pacer-frontend:latest -f ./frontend/Dockerfile ./frontend
	docker build -t $(DOCKER_USERNAME)/map-pacer-backend:latest -f ./backend/Dockerfile .
	docker build -t $(DOCKER_USERNAME)/map-pacer-agent:latest -f ./agent/Dockerfile .
	docker build -t $(DOCKER_USERNAME)/map-pacer-map-service:latest -f ./map-service/Dockerfile .
	docker build -t $(DOCKER_USERNAME)/map-pacer-performance-test:latest -f ./performance-test/Dockerfile ./performance-test
	echo "Pushing images"
	docker push $(DOCKER_USERNAME)/map-pacer-cloud-agent:latest
	docker push $(DOCKER_USERNAME)/map-pacer-frontend:latest
	docker push $(DOCKER_USERNAME)/map-pacer-backend:latest
	docker push $(DOCKER_USERNAME)/map-pacer-agent:latest
	docker push $(DOCKER_USERNAME)/map-pacer-map-service:latest
	docker push $(DOCKER_USERNAME)/map-pacer-performance-test:latest

.PHONY: pdf
pdf:
	sudo docker run --rm -v $(CUR_DIR)/docs/thesis:/data mactat/latex:latest  make pdf

.PHONY: clean
clean:
	kubectl config use-context kind-kind
	tilt down
	kubectl delete --ignore-not-found=true -f ./observability/kube-prometheus/manifests/
	kubectl delete --ignore-not-found=true -f ./observability/kube-prometheus/manifests/setup
