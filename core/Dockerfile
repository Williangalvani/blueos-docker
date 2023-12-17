# Build frontend
FROM --platform=$BUILDPLATFORM oven/bun:1.0.3-slim AS frontendBuilder

ARG VITE_APP_GIT_DESCRIBE
RUN [ -z "$VITE_APP_GIT_DESCRIBE" ] \
    && echo "VITE_APP_GIT_DESCRIBE argument not provided." \
    && echo "Use: --build-arg VITE_APP_GIT_DESCRIBE=\$(git describe --long --always --dirty --all)" \
    && exit 1 || exit 0

COPY frontend /home/pi/frontend
RUN bun install --cwd /home/pi/frontend
RUN bun run --cwd /home/pi/frontend build

# Download binaries
FROM bluerobotics/blueos-base:v0.1.0 as downloadBinaries
COPY tools /home/pi/tools
RUN /home/pi/tools/install-static-binaries.sh

#cockpit
FROM --platform=$BUILDPLATFORM node:18-buster-slim AS cockpitBuilder
RUN mkdir /frontend && ls /frontend

RUN apt update && apt install -y git \
  && git clone --depth 1 --recurse-submodules --branch webrtc https://github.com/williangalvani/cockpit.git /frontend
RUN ls
RUN --mount=type=cache,target=/frontend/node_modules yarn --cwd /frontend install --network-timeout=300000
ARG DEMO_BUILD
RUN --mount=type=cache,target=/frontend/node_modules VITE_DEMO_MODE=$DEMO_MODE yarn --cwd /frontend build

# BlueOS-docker base image
FROM ghcr.io/williangalvani/nvidia-glx-desktop-lite:latest

RUN --mount=type=cache,target=/var/cache/apt sudo apt-get update && \
    sudo apt-get install --assume-yes --no-install-recommends \
    # TOOLS:
        bat \
        bzip2 \
        curl \
        dnsutils \
        exa \
        file \
        htop \
        iotop \
        iproute2 \
        iputils-ping \
        jq \
        less \
        locate \
        lsof \
        nano \
        parallel \
        screen \
        tmux \
        tree \
        unzip \
        vim \
        watch \
        wget \
    # LIBS:
        libatm1 \
        libavcodec58 \
        libavfilter7 \
        libavformat58 \
        libavutil56 \
        libde265-0 \
        libdv4 \
        libglib2.0-0 \
        libjson-glib-1.0-0 \
        libsrtp2-1 \
        libtcl8.6 \
        libtk8.6 \
        libv4l-0 \
        libxml2 \
        mesa-utils \
        libgl1-mesa-glx \
        libgl1-mesa-dri \
        libxkbcommon0 \
        libgstreamer-plugins-bad1.0-0 \
        gstreamer1.0-plugins-ugly \
        gstreamer1.0-rtsp \
        gstreamer1.0 \
        python3 \
        python-is-python3 \
        python3-pip 

# Install necessary tools
COPY tools /home/pi/tools
RUN sudo /home/pi/tools/install-system-tools.sh

# Install custom libraries
COPY libs /home/pi/libs
RUN sudo /home/pi/libs/install-libs.sh

# Set tmux configuration file
COPY configuration/tmux.conf /etc/tmux.conf
COPY configuration/motd /etc/motd

# Install services
COPY services /home/pi/services
RUN sudo /home/pi/services/install-services.sh
COPY start-blueos-core /usr/bin/start-blueos-core
COPY run-service.sh /usr/bin/run-service

# Copy binaries and necessary folders from downloadBinaries to this stage
COPY --from=downloadBinaries \
    /usr/bin/blueos_startup_update \
    /usr/bin/bridges \
    /usr/bin/machineid-cli \
    /usr/bin/mavlink2rest \
    /usr/bin/mavlink-routerd \
    /usr/bin/mavp2p \
    /usr/bin/ttyd \
    /usr/bin/

# Copy frontend built on frontendBuild to this stage
COPY --from=frontendBuilder /home/pi/frontend/dist /home/pi/frontend

# Asserts
## When running, the .config folder in the docker is not accessible,
## since it gets shadowed by the host's `.config` folder.
## If the folder exists during the build step, it means we put it here by mistake.
RUN [ ! -d "/root/.config" ]

ARG GIT_DESCRIBE_TAGS
RUN [ -z "$GIT_DESCRIBE_TAGS" ] \
    && echo "GIT_DESCRIBE_TAGS argument not provided." \
    && echo "Use: --build-arg GIT_DESCRIBE_TAGS=\$(git describe --tags --long --always)" \
    && exit 1 || exit 0

# Update blueosrc with the necessary environment variables
RUN export RCFILE_PATH="/etc/blueosrc"
RUN sudo touch "/etc/blueosrc"
RUN sudo chmod 777 "/etc/blueosrc"
RUN RCFILE_PATH="/etc/blueosrc" \
    && echo "export GIT_DESCRIBE_TAGS=$GIT_DESCRIBE_TAGS" >> $RCFILE_PATH \
    && echo "export HISTFILE=/etc/blueos/.bash_history" >> $RCFILE_PATH \
    && echo "export PATH=/usr/blueos/bin:$PATH" >> $RCFILE_PATH

# create some Symlinks to make life easier
RUN sudo mkdir -p /shortcuts
RUN sudo ln -s /root/.config /shortcuts/configs
RUN sudo ln -s /var/logs/blueos/services /shortcuts/system_logs
RUN sudo ln -s /usr/blueos/userdata /shortcuts/userdata
RUN sudo ln -s /usr/blueos/extensions /shortcuts/extensions
RUN sudo ln -s /root/.config/ardupilot-manager /shortcuts/ardupilot_logs
RUN sudo ln -s / /shortcuts/system_root

LABEL org.opencontainers.image.source="https://github.com/williangalvani/BlueOS-docker"
LABEL org.opencontainers.image.description="Bluesim tests"
LABEL org.opencontainers.image.licenses="GPL-3.0"

COPY supervisord.conf /etc/supervisord.conf
RUN sudo chmod 755 /etc/supervisord.conf

COPY entrypoint.sh /usr/bin/entrypoint.sh
USER 1000
# add symbolic link to bluesim to kde autostart folder
RUN mkdir -p /home/user/.config/autostart
# create a .desktop entry for bluesim at /home/user/.config/autostart
RUN echo "[Desktop Entry]" > /home/user/.config/autostart/bluesim.desktop
RUN echo "Type=Application" >> /home/user/.config/autostart/bluesim.desktop
RUN echo "Exec=/home/pi/bluesim/BlueSim.x86_64 --no-sitl --pool" >> /home/user/.config/autostart/bluesim.desktop
RUN echo "Hidden=false" >> /home/user/.config/autostart/bluesim.desktop
RUN echo "NoDisplay=false" >> /home/user/.config/autostart/bluesim.desktop
RUN echo "Name=BlueSim" >> /home/user/.config/autostart/bluesim.desktop

# add cockpit
RUN sudo wget https://github.com/TheWaWaR/simple-http-server/releases/download/v0.6.6/x86_64-unknown-linux-musl-simple-http-server \
    -O /usr/bin/simple-http-server
RUN sudo chmod 777 /usr/bin/simple-http-server
COPY --from=cockpitBuilder /frontend/dist /cockpit


COPY bluesim-x86 /home/pi/bluesim
RUN sudo chmod +x /home/pi/bluesim/BlueSim.x86_64

RUN sudo mkdir -p /root/.config/mavlink-camera-manager/
COPY settings/camera-settings.json /root/.config/mavlink-camera-manager/settings.json
COPY settings/bag-of-holding /root/.config/
COPY tools/mavlink_camera_manager/mavlink-camera-manager-linux-desktop /usr/bin/mavlink-camera-manager
RUN sudo chmod +x /usr/bin/mavlink-camera-manager
EXPOSE 8080
COPY settings/eeprom.bin /root/.config/ardupilot-manager/firmware/eeprom.bin

ENV SHELL /bin/bash
ENV USER user
WORKDIR /home/user

ENTRYPOINT ["/usr/bin/entrypoint.sh"]