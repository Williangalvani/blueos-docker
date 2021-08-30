#!/usr/bin/env bash

apt update && apt install -y curl
curl -fsSL https://code-server.dev/install.sh | sh
