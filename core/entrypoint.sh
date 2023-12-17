#!/bin/bash

export BLUEOS_COCKPIT_PORT=$VAST_TCP_PORT_70000
export BLUEOS_SIGNALING_SERVER_PORT=$VAST_TCP_PORT_70001

printenv | grep '^VAST' > /tmp/env.txt
printenv | grep '^BLUEOS' >> /tmp/env.txt
printenv | grep '^PUBLIC_IP' >> /tmp/env.txt
# setup query params for cockpit
sudo jq '. + {"extra_query": "mainConnectionURI=ws://'"$PUBLIC_IPADDR"':'"$VAST_TCP_PORT_80"'/mavlink2rest/ws/mavlink&webRTCSignallingURI='"ws://$PUBLIC_IPADDR"':'"$BLUEOS_SIGNALING_SERVER_PORT"'"}' /cockpit/register_service > temp.json && sudo mv temp.json /cockpit/register_service
sudo bash -c "set -a && source /tmp/env.txt && set +a && /usr/bin/start-blueos-core"
/usr/bin/supervisord