#!/usr/bin/env bash
# generate the textfile of my messages
hpi query my.discord.messages -s "$@" | jq -r .content >/tmp/discord.txt
