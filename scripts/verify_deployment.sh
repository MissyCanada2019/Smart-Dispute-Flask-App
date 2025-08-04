#!/bin/bash

# Deployment Verification Script
# Checks integrity of critical files after deployment

# List of files to verify
FILES=(
  "utils/legal_journey.py"
  "main.py"
  "utils/__init__.py"
)

# Create checksums
echo "Creating file checksums..."
md5sum "${FILES[@]}" > .file_checksums

# Verify checksums after deployment
echo "Verifying file integrity..."
if md5sum -c .file_checksums; then
  echo "All files verified successfully"
else
  echo "ERROR: File corruption detected!"
  exit 1
fi