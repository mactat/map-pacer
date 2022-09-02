# Define required macros here
SHELL = /bin/bash
include .env
export

define PROJECT_HELP_MSG
Makefile for map-pacer project
For spinning dev-env, tilt, kind and ctlptl has to be configured.
For cloud development add '.env' file with AZURE_SUBSCRIPTION_ID, AZURE_GROUP_NAME, AZURE_CLUSTER_NAME

Usage:
	make dev                    run dev cluster and tilt
	make clean                  stop local cluster and tilt
	make cloud-login            login to azure and setup kubectl
	make cloud-up               start kubernetes cluster in azure
	make cloud-down             stop kubernetes cluster in azure
	make cloud-deploy           deploy to kubernetes cluster in azure
endef

export PROJECT_HELP_MSG

help:
	echo "$$PROJECT_HELP_MSG" | less


.PHONY: dev
dev:
	tilt up

.PHONY: cloud-login
cloud-login:
	# Login to the cloud
	az login --use-device-code

	# Set connection details
	az account set --subscription $(AZURE_SUBSCRIPTION_ID)
	az aks get-credentials --resource-group $(AZURE_GROUP_NAME) --name $(AZURE_CLUSTER_NAME)

	# Check the context
	echo "Current context:"
	kubectl config current-context

.PHONY: cloud-up
cloud-on:
	# Start the cluster
	az aks start --name $(AZURE_CLUSTER_NAME) --resource-group $(AZURE_GROUP_NAME)

.PHONY: cloud-down
cloud-off:
	# Stop the cluster
	az aks stop --name $(AZURE_CLUSTER_NAME) --resource-group $(AZURE_GROUP_NAME)

.PHONY: cloud-deploy
cloud-deploy:
    # Deploy to the cluster
	echo "deploying to cluster"

.PHONY: clean
clean:
	tilt down
