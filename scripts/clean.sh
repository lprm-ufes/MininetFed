#!/bin/bash

# Para e remove apenas os contêineres Docker com imagens prefixadas por "mininetfed:"
containers=$(sudo docker ps -a --filter "ancestor=mininetfed" --format "{{.ID}}")
if [ -n "$containers" ]; then
    sudo docker stop $containers
    sudo docker rm $containers
fi

# Limpa o ambiente Mininet
sudo mn -c
