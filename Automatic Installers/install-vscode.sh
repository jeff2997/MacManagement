#!/bin/bash

###################################################
# VSCode Auto-Updater
# Jeff Pearson
# June 4, 2020
# This script downloads and parses the html from 
# Microsoft's website to always install the 
# lastest version of VSCode
###################################################

#Get the current version from a reputable link that updates with each version
mkdir /Library/Application\ Support/vscodeinstaller
curl -L https://code.visualstudio.com/updates --output /Library/Application\ Support/vscodeinstaller/code.html

# Grab the url from the mess of HTML
url_universal=$(cat /Library/Application\ Support/vscodeinstaller/code.html | grep -o 'https://update.code.visualstudio.com/[0-9].[0-9][0-9].[0-9]/darwin-universal/stable')
# url_arm64=$(cat /Library/Application\ Support/vscodeinstaller/code.html | grep -o 'https://update.code.visualstudio.com/[0-9].[0-9][0-9].[0-9]/darwin-arm64/stable')
# url_intel=$(cat /Library/Application\ Support/vscodeinstaller/code.html | grep -o 'https://update.code.visualstudio.com/[0-9].[0-9][0-9].[0-9]/darwin/stable')

# Download the installer
curl -L $url_universal --output /Library/Application\ Support/vscodeinstaller/vscode.zip

# Delete the old app if it exists
if [ -d /Applications/Visual\ Studio\ Code.app ]; then
    rm -rf /Applications/Visual\ Studio\ Code.app
fi

# Install the new one
unzip /Library/Application\ Support/vscodeinstaller/vscode.zip -d /Applications

# Clean up
rm -rf /Library/Application\ Support/vscodeinstaller