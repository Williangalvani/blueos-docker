#!/usr/bin/env bash
# Script to install tools that are simple static binaries

# Immediately exit on errors
set -e

# Any changes in this file should reflect in the Dockerfile as well,
# since we get this binaries from multstage
TOOLS=(
    blueos_startup_update
    bridges
    linux2rest
    mavlink2rest
    mavlink_router
    mavp2p
    ttyd
)

parallel --halt now,fail=1 '/home/pi/tools/{}/bootstrap.sh' ::: "${TOOLS[@]}"
