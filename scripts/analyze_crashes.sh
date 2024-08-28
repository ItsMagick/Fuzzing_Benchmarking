#!/bin/bash
set -ex

MOSQUITTO_BINARY="binaries/mosquitto"
AFLNET_REPLAY_BINARY="binaries/aflnet-replay"
TESTCASE_DIR="out2/preload/replayable-crashes"
LOG_FILE="aflnet_crashes.log"
MOSQUITTO_PORT=1885
GDB_SCRIPT="gdb_commands.txt"

echo "set pagination off" > $GDB_SCRIPT
echo "run -p $MOSQUITTO_PORT" >> $GDB_SCRIPT

> $LOG_FILE

for testcase in $TESTCASE_DIR/*; do
    echo "Running testcase: $testcase" | tee -a $LOG_FILE
    gnome-terminal -- bash -c "gdb -q $MOSQUITTO_BINARY -x $GDB_SCRIPT; exec bash"
    wait
    $AFLNET_REPLAY_BINARY "$testcase" MQTT $MOSQUITTO_PORT
    echo "Testcase completed: $testcase"
    echo "---------------------------------"
done
echo "All test cases have been executed. You can analyze the crashes in the gdb terminal."
