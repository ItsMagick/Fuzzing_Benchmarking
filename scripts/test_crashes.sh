#!/bin/bash

MOSQUITTO_BINARY="binaries/mosquitto"
AFLNET_REPLAY_BINARY="binaries/aflnet-replay"
TESTCASE_DIR="out2/preload/replayable-crashes"
LOG_FILE="aflnet_crashes.log"
MOSQUITTO_PORT=1885

echo "set pagination off" > $GDB_SCRIPT
echo "run -p $MOSQUITTO_PORT" >> $GDB_SCRIPT

start_mosquitto() {
    $MOSQUITTO_BINARY -p $MOSQUITTO_PORT 2>> $LOG_FILE &
    MOSQUITTO_PID=$!
    sleep 2
}

stop_mosquitto() {
    kill $MOSQUITTO_PID
    while ps -p $MOSQUITTO_PID > /dev/null; do
        sleep 1
    done
}

> $LOG_FILE

for testcase in $TESTCASE_DIR/*; do
    echo "Running testcase: $testcase" | tee -a $LOG_FILE
    start_mosquitto
    $AFLNET_REPLAY_BINARY "$testcase" MQTT $MOSQUITTO_PORT 2>> $LOG_FILE
    stop_mosquitto
    echo "Waiting for system resources to be freed..."
    sleep 5  # Additional sleep to ensure port resources are freed


    echo -e "Testcase completed: $testcase" | tee -a $LOG_FILE
    echo "---------------------------------" | tee -a $LOG_FILE
done

echo "All test cases have been executed. Crashes (if any) have been logged to $LOG_FILE."
tar -czvf aflnet_crashes.tar.gz $LOG_FILE
git add aflnet_crashes.tar.gz