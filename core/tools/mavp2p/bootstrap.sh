#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

LOCAL_BINARY_PATH="/usr/bin/mavp2p"
VERSION="v1.1.1"
GITHUB_REMOTE="https://github.com/bluenviron/mavp2p"

# By default we install armv6
REMOTE_BINARY_URL="${GITHUB_REMOTE}/releases/download/${VERSION}/mavp2p_v1.1.1_linux_armv7.tar.gz"
if [[ "$(uname -m)" == "x86_64"* ]]; then
  REMOTE_BINARY_URL="${GITHUB_REMOTE}/releases/download/${VERSION}/mavp2p_v1.1.1_linux_amd64.tar.gz"
fi

ARTIFACT_NAME="mavp2p"
COMPRESS_FILE="$ARTIFACT_NAME.tar.gz"
wget "$REMOTE_BINARY_URL" -O "$COMPRESS_FILE"
tar -xf "$COMPRESS_FILE"
# Binary
cp "$ARTIFACT_NAME" "$LOCAL_BINARY_PATH"
chmod +x "$LOCAL_BINARY_PATH"

# Remove temporary files
rm -rf "$COMPRESS_FILE" "${ARTIFACT_NAME}"