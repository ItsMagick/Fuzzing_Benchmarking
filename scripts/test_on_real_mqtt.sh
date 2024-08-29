#!/bin/bash
set -ex
AFLNET_REPLAY_BINARY="binaries/aflnet-replay"
TESTCASE_DIR="out2/preload/replayable-crashes"
MOSQUITTO_PORT=1886

for testcase in $TESTCASE_DIR/*; do
    echo "Running testcase: $testcase"
    $AFLNET_REPLAY_BINARY "$testcase" MQTT $MOSQUITTO_PORT
    echo -e "Testcase completed: $testcase"

done
