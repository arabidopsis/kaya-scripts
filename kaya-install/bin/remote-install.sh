#!/bin/bash
if [ "$#" -eq 0 ]; then
    echo "No machine specified"
fi
MACHINE=$1
TGT=kaya-dist
rm -rf dist
uv build
scp -q -r dist $MACHINE:$TGT
ssh $MACHINE "PATH=~/.local/bin uv tool uninstall kaya-install"
ssh $MACHINE "PATH=~/.local/bin uv tool install --find-links $TGT kaya-install && rm -rf $TGT"