#!/bin/bash
if [ "$#" -eq 0 ]; then
    echo "No machine specified"
    exit 1
fi
MACHINE=$1
TGT=kaya-install
rm -rf dist
uv build
scp -q -r dist $MACHINE:${TGT}-dist
ssh $MACHINE "PATH=~/.local/bin uv tool uninstall ${TGT}"
ssh $MACHINE "PATH=~/.local/bin uv tool install --find-links ${TGT}-dist ${TGT} && rm -rf ${TGT}-dist"