#!/bin/bash
# Build script to run inside Docker container

set -e

SPEC_FILE=$1

if [ -z "$SPEC_FILE" ]; then
    echo "Usage: $0 <spec-file>"
    exit 1
fi

echo "Building RPM from $SPEC_FILE"

# Copy SPEC file
cp "/mnt/specs/$(basename $SPEC_FILE)" ~/rpmbuild/SPECS/

# Download sources
cd ~/rpmbuild/SPECS
spectool -g -R "$(basename $SPEC_FILE)"

# Build RPM
rpmbuild -ba "$(basename $SPEC_FILE)"

echo "Build complete"
