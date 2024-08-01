#!/bin/bash
set -ex
echo "Grab a Coffee. This might take some time. We are now building Mosquitto and AFLNet from source."
docker build -t aflnet --output=./binaries --target=binaries . $@