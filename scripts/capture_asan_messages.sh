#!/bin/bash

PROCESS_NAME="./binaries/mosquitto"
LOG_FILE="process_monitor.log"
CRASH_LOG="process_crash.log"
APPLICATION_OUTPUT="application_output.log"
READY_FILE="mosquitto_ready.signal"

timestamped_output() {
    while IFS= read -r line; do
        echo "$(date +"[%Y-%m-%d %H:%M:%S]") $line"
    done
}

start_application() {
    ($PROCESS_NAME 2>&1 | timestamped_output | tee "$APPLICATION_OUTPUT") &
    echo $! > pid_file.txt
}

> "$READY_FILE"

start_application

echo "READY" > "$READY_FILE"

while true; do
    PID=$(cat pid_file.txt)

    if ps -f "$PID" > /dev/null; then
        echo "$(date +"[%Y-%m-%d %H:%M:%S]") - $PROCESS_NAME is running with PID $PID" >> "$LOG_FILE"
    else
        echo "$(date +"[%Y-%m-%d %H:%M:%S]") - $PROCESS_NAME has crashed or is not running" >> "$CRASH_LOG"
        echo "$(date +"[%Y-%m-%d %H:%M:%S]") - Crash details:" >> "$CRASH_LOG"
        cat "$APPLICATION_OUTPUT" >> "$CRASH_LOG"
        echo "" >> "$CRASH_LOG"  # Add a newline for readability
        break
        # Optionally,  the application
    fi
done

echo "$(date +"[%Y-%m-%d %H:%M:%S]") - Exiting script as the process is no longer running." >> "$LOG_FILE"
rm mosquitto_ready.signal