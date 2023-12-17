#!/bin/sh
echo -ne '\033c\033]0;BlueSim\a'
base_path="$(dirname "$(realpath "$0")")"
"$base_path/BlueSim.x86_64" "$@"
