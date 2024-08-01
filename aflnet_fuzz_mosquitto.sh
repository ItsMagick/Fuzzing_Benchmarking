#!/bin/bash

set -ex
./binaries/afl-fuzz -d -m none -i ./aflnet/tutorials/mosquitto/in-mqtt -o out -N tcp://127.0.0.1/1883 -P MQTT -D 10000 -q 3 -s 3 -E -K -R ./binaries/mosquitto &
./capture_traffic.sh