#!/bin/bash

export BLUEOS_COCKPIT_PORT=${VAST_TCP_PORT_70000:-6042}
export BLUEOS_SIGNALING_SERVER_PORT=${VAST_TCP_PORT_70001:-6041}
if [ -z "$PUBLIC_IPADDR" ]; then
  export PUBLIC_IPADDR=$(curl ifconfig.me)
fi

printenv | grep '^VAST' > /tmp/env.txt
printenv | grep '^BLUEOS' >> /tmp/env.txt
printenv | grep '^PUBLIC_IP' >> /tmp/env.txt
printenv | grep '^DISPLAY' >> /tmp/env.txt
printenv | grep '^CDEPTH' >> /tmp/env.txt
printenv | grep '^SIZEH' >> /tmp/env.txt
printenv | grep '^SIZEW' >> /tmp/env.txt
printenv | grep '^DPI' >> /tmp/env.txt
printenv | grep '^REFRESH' >> /tmp/env.txt
printenv | grep '^VIDEO_PORT' >> /tmp/env.txt
printenv | grep '^BASIC_AUTH_PASSWORD' >> /tmp/env.txt
printenv | grep '^WEBRTC' >> /tmp/env.txt
printenv | grep '^TURN' >> /tmp/env.txt
printenv | grep '^TZ' >> /tmp/env.txt


echo 'PASSWD=mypasswd' >> /tmp/env.txt

# setup query params for cockpit
sudo jq '. + {"extra_query": "mainConnectionURI=ws://'"$PUBLIC_IPADDR"':'"$VAST_TCP_PORT_80"'/mavlink2rest/ws/mavlink&webRTCSignallingURI='"ws://$PUBLIC_IPADDR"':'"$BLUEOS_SIGNALING_SERVER_PORT"'"}' /cockpit/register_service > temp.json && sudo mv temp.json /cockpit/register_service
sudo bash -c "set -a && source /tmp/env.txt && set +a && /usr/bin/start-blueos-core"
/usr/bin/supervisord