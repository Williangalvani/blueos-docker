#!/usr/bin/env bash


BUILD_PACKAGES=(
    build-essential
    pkg-config
    git
    jq
    curl
)


apt update && apt install --no-install-recommends -y ${BUILD_PACKAGES[*]} libx11-dev libxkbfile-dev libsecret-1-dev libatomic1

if [[ "$(uname -m)" != "x86_64"* ]]; then

    wget https://nodejs.org/dist/v14.16.1/node-v14.16.1-linux-armv7l.tar.gz
    tar -xzf node-v14.16.1-linux-armv7l.tar.gz
    cp -R node-v14.16.1-linux-armv7l/* /usr/local/
    rm -r node-v14.16.1-linux-armv7l*
    npm install -g code-server --unsafe-perm
fi

if [[ "$(uname -m)" == "x86_64"* ]]; then
    curl -fsSL https://code-server.dev/install.sh | sh
fi
rm -r /root/.config/code-server || true

apt -y remove ${BUILD_PACKAGES[*]}
apt -y autoremove
apt -y clean
