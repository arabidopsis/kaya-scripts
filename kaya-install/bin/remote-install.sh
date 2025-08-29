#!/bin/bash
TGT=kaya-dist
rm -rf dist
uv build
scp -q -r dist onycis:$TGT
ssh onycis "PATH=~/.local/bin uv tool uninstall kaya-install"
ssh onycis "PATH=~/.local/bin uv tool install --find-links $TGT kaya-install && rm -rf $TGT"