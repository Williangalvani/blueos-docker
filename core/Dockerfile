# Build frontend
FROM --platform=$BUILDPLATFORM oven/bun:1.0.3-slim AS frontend-builder

ARG VITE_APP_GIT_DESCRIBE
ENV VITE_APP_GIT_DESCRIBE=${VITE_APP_GIT_DESCRIBE:-none/none-0-g00000000}
RUN <<-EOF
set -e

    if [ -z "$VITE_APP_GIT_DESCRIBE" ]; then
        echo "VITE_APP_GIT_DESCRIBE argument not provided."
        echo "Use: --build-arg VITE_APP_GIT_DESCRIBE=\$(git describe --long --always --dirty --all)"
        exit 1
    fi

EOF

COPY frontend /home/pi/frontend
RUN <<-EOF
set -e

    bun install --cwd /home/pi/frontend
    bun run --cwd /home/pi/frontend build

EOF

FROM bluerobotics/blueos-base:0.2.1 AS base

# Download binaries
FROM base AS download-binaries
COPY tools /home/pi/tools
RUN /home/pi/tools/install-static-binaries.sh

#cockpit
FROM --platform=$BUILDPLATFORM node:20-buster-slim AS cockpitBuilder
RUN mkdir /frontend && ls /frontend && echo "why"

RUN apt update && apt install -y git \
  && ls && git clone --depth 1 --recurse-submodules  https://github.com/bluerobotics/cockpit.git /frontend
RUN yarn --cwd /frontend install --network-timeout=300000
ARG DEMO_BUILD
RUN VITE_DEMO_MODE=$DEMO_MODE yarn --cwd /frontend build

# BlueOS-docker base image
FROM williangalvani/nvidia-glx-desktop-lite:shrinking_plus_blueos_dev

# Define arguments for target platform
# These arguments are defined automatically by buildx when using `--platform`
ARG TARGETARCH
ARG TARGETVARIANT

# Ensure that the git describe exists and also is in valid format as well
# The format can be invalid if someone is build BlueOS without a tag as reference
ARG GIT_DESCRIBE_TAGS
ENV GIT_DESCRIBE_TAGS=${GIT_DESCRIBE_TAGS:-0.0.0-0-g00000000}
RUN <<-EOF
set -e

    if [ -z "$GIT_DESCRIBE_TAGS" ]; then
        echo "GIT_DESCRIBE_TAGS argument not provided."
        echo "Use: --build-arg GIT_DESCRIBE_TAGS=\$(git describe --tags --long --always)"
        exit 1
    fi

    if [[ ! $GIT_DESCRIBE_TAGS =~ -[0-9]+-g[a-f0-9]{8}$ ]]; then
        echo "Invalid format: $GIT_DESCRIBE_TAGS (E.g: <TAG>-<COMMIT_NUMBER>-g<SHORT_HASH>)"
        exit 1
    fi

EOF

# Set these arguments as environment variables
ENV TARGETARCH=${TARGETARCH}
ENV TARGETVARIANT=${TARGETVARIANT}

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

# Copy binaries and necessary folders from download-binaries to this stage
COPY --from=download-binaries \
    /usr/bin/blueos_startup_update.py \
    /usr/bin/bridges \
    /usr/bin/machineid-cli \
    /usr/bin/mavlink2rest \
    /usr/bin/mavlink-routerd \
    /usr/bin/mavlink-server \
    /usr/bin/zenoh \
    /usr/bin/mavp2p \
    /usr/bin/ttyd \
    /usr/bin/

# Copy frontend built on frontend-builder to this stage
COPY --from=frontend-builder /home/pi/frontend/dist /home/pi/frontend

RUN <<-EOF
set -e

    # Asserts
    ## When running, the .config folder in the docker is not accessible,
    ## since it gets shadowed by the host's `.config` folder.
    ## If the folder tree contains any files during the build step, it means we put it here by mistake.
    [ -z "$(find '/root/.config' -mindepth 1 -type f)" ]

    # Update blueosrc with the necessary environment variables
    RCFILE_PATH="/etc/blueosrc"
    echo "export GIT_DESCRIBE_TAGS=$GIT_DESCRIBE_TAGS" | sudo tee -a $RCFILE_PATH
    echo "export HISTFILE=/etc/blueos/.bash_history" | sudo tee -a $RCFILE_PATH
    echo "export PATH=$(python -m site --user-base)/bin:/usr/blueos/bin:$PATH" | sudo tee -a $RCFILE_PATH

    # Setup shortcuts
    sudo mkdir -p /shortcuts
    sudo ln -s /root/.config /shortcuts/configs
    sudo ln -s /var/logs/blueos/services /shortcuts/system_logs
    sudo ln -s /usr/blueos/userdata /shortcuts/userdata
    sudo ln -s /usr/blueos/extensions /shortcuts/extensions
    sudo ln -s /root/.config/ardupilot-manager /shortcuts/ardupilot_logs
    sudo ln -s / /shortcuts/system_root

    # Setup user
    sudo useradd -m -G dialout blueos

    # Remove /etc/dhcpcd.conf if it exists inside the docker
    # This is to prevent an awkward behavior where docker doesnt find the file
    # on the host system and creates a folder instead, but tries to mount the folder
    # on top of the existing file inside the docker.
    # This allows docker to actually create a folder, which we handle in networksetup.py
    # rm -f /etc/dhcpcd.conf

EOF

ARG DEMO_BUILD

# Update blueosrc with the necessary environment variables
RUN export RCFILE_PATH="/etc/blueosrc"
RUN sudo touch "/etc/blueosrc"
RUN sudo chmod 777 "/etc/blueosrc"
RUN RCFILE_PATH="/etc/blueosrc" \
    && echo "export GIT_DESCRIBE_TAGS=$GIT_DESCRIBE_TAGS" >> $RCFILE_PATH \
    && echo "export HISTFILE=/etc/blueos/.bash_history" >> $RCFILE_PATH \
    && echo "export PATH=/usr/blueos/bin:$PATH" >> $RCFILE_PATH \
    && echo "export BLUEOS_DEMO_MODE=$DEMO_BUILD" >> $RCFILE_PATH

LABEL org.opencontainers.image.source="https://github.com/williangalvani/BlueOS-docker"
LABEL org.opencontainers.image.description="Bluesim tests"
LABEL org.opencontainers.image.licenses="GPL-3.0"

COPY supervisord.conf /etc/supervisord.conf
RUN sudo chmod 755 /etc/supervisord.conf

COPY entrypoint.sh /usr/bin/entrypoint.sh
USER 1000

RUN sudo mkdir -p /etc/xdg/lxsession/LXDE && echo "@/home/pi/bluesim/BlueSim.x86_64 --pool --no-sitl" | sudo tee -a /etc/xdg/lxsession/LXDE/autostart

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
EXPOSE 8080
COPY settings/eeprom.bin /root/.config/ardupilot-manager/firmware/eeprom.bin

ENV SHELL /bin/bash
ENV USER user
WORKDIR /home/user

ENTRYPOINT ["/usr/bin/entrypoint.sh"]
