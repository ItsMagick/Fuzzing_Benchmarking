#!/bin/bash
set -ex

INTERFACE=lo
OUTPUT_DIR=./traffic
DURATION=60
AFLNET_PROCESS_PATTERN="afl-fuzz"

mkdir -p $OUTPUT_DIR

while true; do
  if pgrep -f $AFLNET_PROCESS_PATTERN > /dev/null; then
    FILENAME=$(date +"$OUTPUT_DIR/fuzzing_traffic_%Y%m%d%H%M%S.pcap")
    sudo tcpdump -i $INTERFACE -w $FILENAME tcp port 1883 &
    PID=$!
    sleep $DURATION
    sudo kill $PID
  else
    echo "No AFLNet process found... Getting the fuck outa here"
    exit 1
  fi
done
