#!/bin/bash

printenv > /tmp/env.txt
sudo bash -c "source /tmp/env.txt && /usr/bin/start-blueos-core"
sudo /usr/bin/start-blueos-core &&
/usr/bin/supervisord