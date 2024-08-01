#!/bin/bash
set -ex
# Define paths
PATCH_FILE="./afl-llvm-pass.patch"
TARGET_FILE="afl-llvm-pass.so.cc"

# Apply the patch
echo "Applying patch to $TARGET_FILE..."
patch < $PATCH_FILE

# Check if the patch was applied successfully
if [ $? -eq 0 ]; then
  echo "Patch applied successfully."
else
  echo "Failed to apply patch."
  exit 1
fi