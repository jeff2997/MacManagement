#!/bin/bash

###################################################
# Brave Auto-Updater
# Jeff Pearson
# June 4, 2020
# This script installs or updates the Brave browser
###################################################


# URL
url_arm64="https://laptop-updates.brave.com/latest/osxarm64/release"
url_intel="https://laptop-updates.brave.com/latest/osx/release"

# Other Variables
architecture=$(/usr/bin/arch)

if [[ ! -d /var/tmp/braveinstaller ]]; then
    mkdir /var/tmp/braveinstaller
fi

if [[ "$architecture" == "arm64" ]]; then
    echo "Apple Silicon Architecture Detected"
    curl -L $url_arm64 --output /var/tmp/braveinstaller/brave.dmg
else # Probably intel
    echo "Intel Architecture Detected"
    curl -L $url_intel --output /var/tmp/braveinstaller/brave.dmg
fi

# Quit if running
if ! [[ "$(ps aux | grep Brave | grep -v grep)" == "" ]]; then
    killall "Brave Browser"
fi

# Delete the old one if it exists
if [ -d "/Applications/Brave Browser.app" ]; then
    echo "Deleting old Brave Browser"
    rm -rf "/Applications/Brave\ Browser.app"
fi

# Install the new one
echo "Mounting disk image"
hdiutil attach /var/tmp/braveinstaller/brave.dmg -mountpoint /Volumes/brave -quiet
echo "Copying Files"
cp -r "/Volumes/brave/Brave Browser.app" /Applications
echo "Done copying - cleaning up."

# Clean up
umount /Volumes/brave
rm -rf /var/tmp/braveinstaller
echo "Done!"