#!/bin/bash

printenv | grep '^VAST' > /tmp/env.txt
sudo bash -c "set -a && source /tmp/env.txt && set +a && /usr/bin/start-blueos-core"
/usr/bin/supervisord