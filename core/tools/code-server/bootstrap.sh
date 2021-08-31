#!/usr/bin/env bash

apt update && apt install -y curl libatomic1

if [[ "$(uname -m)" != "x86_64"* ]]; then

    wget https://nodejs.org/dist/v14.16.1/node-v14.16.1-linux-armv7l.tar.gz
    tar -xzf node-v14.16.1-linux-armv7l.tar.gz
    cp -R node-v14.16.1-linux-armv7l/* /usr/local/
    rm -r node-v14.16.1-linux-armv7l*
    npm install -g code-server
fi

if [[ "$(uname -m)" == "x86_64"* ]]; then
    curl -fsSL https://code-server.dev/install.sh | sh
fi
rm -r /root/.config/code-server || true
