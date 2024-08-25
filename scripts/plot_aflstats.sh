#!/bin/bash
set -ex
BASE_DIR=$(git rev-parse --show-toplevel)
AFL_PLOT=$BASE_DIR/binaries/afl-plot
PRELOAD_DIR=$BASE_DIR/plots/preload
MAIN_DIR=$BASE_DIR/plots/main
BASE_OUT_DIR=$BASE_DIR/out2

$AFL_PLOT $BASE_OUT_DIR/main $MAIN_DIR
$AFL_PLOT $BASE_OUT_DIR/preload $PRELOAD_DIR