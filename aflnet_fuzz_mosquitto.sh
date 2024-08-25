#!/bin/bash

set -ex
#export LD_PRELOAD=./preload_redirect.so
./binaries/afl-fuzz -d -m none -i aflnet_in -o out2 -N tcp://127.0.0.1/1883 -P MQTT -D 10000 -q 3 -s 3 -E -K -R ./binaries/mosquitto
#./extract_afl_exec_speeds.sh &
