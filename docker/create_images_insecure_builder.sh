#!/bin/bash


sudo docker buildx create --driver-opt image=moby/buildkit:master  \
                     --use --name insecure-builder \
                     --buildkitd-flags '--allow-insecure-entitlement security.insecure'
sudo docker buildx use insecure-builder


sudo docker buildx build -o type=docker --allow security.insecure --tag "mininetfed:broker" -f docker/Dockerfile.broker . 
sudo docker buildx build -o type=docker --allow security.insecure --tag "mininetfed:client" -f docker/Dockerfile.client .
sudo docker buildx build -o type=docker --allow security.insecure --tag "mininetfed:server" -f docker/Dockerfile.server .
sudo docker buildx build -o type=docker --allow security.insecure --tag "mininetfed:serversensor" -f docker/Dockerfile.serversensor .
sudo docker buildx build -o type=docker --allow security.insecure --tag "mininetfed:clientsensor" -f docker/Dockerfile.clientsensor .
sudo docker buildx rm insecure-builder