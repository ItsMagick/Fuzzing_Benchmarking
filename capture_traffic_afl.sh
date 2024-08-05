#!/bin/bash
set -ex

INTERFACE=lo
TRAFFIC_OUTPUT_DIR=./traffic
AFL_OUTPUT_DIR=./out
DURATION=60
AFLNET_PROCESS_PATTERN="afl-fuzz"

mkdir -p $TRAFFIC_OUTPUT_DIR

while true; do
  if pgrep -f $AFLNET_PROCESS_PATTERN > /dev/null; then
    python3 extract_alf_exec_speed.py "$AFL_OUTPUT_DIR/fuzzer_stats"
    FILENAME=$(date +"$TRAFFIC_OUTPUT_DIR/fuzzing_traffic_%Y%m%d%H%M%S.pcap")
    sudo tcpdump -i $INTERFACE -w $FILENAME tcp port 1883 &
    PID=$!
    sleep $DURATION
    sudo kill $PID
  else
    echo "No AFLNet process found... Ima head out..."
    exit 1
  fi
done
