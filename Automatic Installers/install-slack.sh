#!/bin/bash
tmp_mount=`/usr/bin/mktemp -d /tmp/slack.XXXX`

if ! [ -d "/Library/Application Support/ITCache" ]; then
    mkdir "/Library/Application Support/ITCache"
fi

kill $(ps -ax | grep Slack.app/Contents/MacOS/Slack | grep -v "grep" | head -n 1 | awk '{ print $1 }')

curl -L https://slack.com/ssb/download-osx -o "/Library/Application Support/ITCache/slack-current.dmg"

rm -dfR "/Applications/Slack.app"

hdiutil attach "/Library/Application Support/ITCache/slack-current.dmg" -nobrowse -quiet -mountpoint "${tmp_mount}"

ditto "${tmp_mount}/Slack.app" "/Applications/Slack.app"
sleep 1
hdiutil detach ${tmp_mount}

rm -rf "/Library/Application Support/ITCache/slack-current.dmg"