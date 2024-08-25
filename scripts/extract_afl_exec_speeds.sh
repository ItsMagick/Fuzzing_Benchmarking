#!/bin/bash
set -ex

TRAFFIC_OUTPUT_DIR=../traffic
AFL_OUTPUT_DIR=../out
DURATION=60
PROCESS_PATTERN="afl-fuzz"

mkdir -p $TRAFFIC_OUTPUT_DIR

while true; do
  if pgrep -f $PROCESS_PATTERN > /dev/null; then
    python3 extract_alf_exec_speed.py "$AFL_OUTPUT_DIR/fuzzer_stats"
    PID=$!
    sleep $DURATION
    sudo kill $PID
  else
    echo "No AFLNet process found... Ima head out..."
    exit 1
  fi
done
