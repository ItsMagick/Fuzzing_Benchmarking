#!/bin/bash
set -ex

INTERFACE=lo
TRAFFIC_OUTPUT_DIR=../traffic
DURATION=900
PROCESS_PATTERN="mosquitto"
mkdir -p $TRAFFIC_OUTPUT_DIR

while true; do
  if pgrep -f $PROCESS_PATTERN > /dev/null; then
    FILENAME=$(date +"$TRAFFIC_OUTPUT_DIR/mqtt_states_%Y%m%d%H%M%S.pcap")
    sudo tcpdump -i $INTERFACE -w $FILENAME tcp port 1883 &
    PID=$!
    sleep $DURATION
    sudo kill $PID
  else
    echo "No $PROCESS_PATTERN process found... Ima head out..."
    exit 1
  fi
done
