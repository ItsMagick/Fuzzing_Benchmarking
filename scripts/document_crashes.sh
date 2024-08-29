#!/bin/bash
set -ex

directory="out2/preload/replayable-crashes"
output_file="dump/crashes_documentation.txt"
start_descriptor="id:000009,sig:06,src:000158,op:havoc,rep:64"
start_writing=false
for file in $directory/*; do
    file_descriptor=$(basename "$file")
    if [[ "$file_descriptor" == "$start_descriptor" ]]; then
        start_writing=true
    fi
    if $start_writing; then
        echo "test case $file_descriptor" >> "$output_file"
    fi
done
