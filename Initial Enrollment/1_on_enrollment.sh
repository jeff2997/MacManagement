#!/bin/zsh

# constants
jamfbinary=$(/usr/bin/which jamf)
logFile="/var/log/on_enrollment.log"


# Install Rosetta 2 if necessary
echo "$(date) Detecting CPU Architecture..." >> $logFile
architecture=$(/usr/bin/arch)
if [[ "$architecture" = "arm64" ]]; then
	echo "$(date) Apple Silicon Mac detected, installing Rosetta 2" >> $logFile
	/usr/sbin/softwareupdate --install-rosetta --agree-to-license
    if [[ $? -eq 0 ]]; then
		echo "$(date) Rosetta 2 installed" >> $logFile
    else
    	echo "$(date) Rosetta 2 installation failed! Cannot continue - exiting" >> $logFile
        exit 1
    fi
    sleep 30
else
	echo "$(date) Non-Apple-Silicon platform detected, not installing Rosetta 2" >> $logFile
fi


# Caffeinate to prevent sleep
caffeinate &

# Install Python 3
echo "$(date) Installing Python 3" >> $logFile
${jamfbinary} policy -event "install-python3"

# Drop Branding for DEPNotify
echo "$(date) Dropping Icon for DEPNotify" >> $logFile
${jamfbinary} policy -event "drop-branding"

# Install PySimpleGUI
echo "$(date) Installing PySimpleGUI" >> $logFile
/usr/local/bin/python3 -m pip install PySimpleGUI

# Install Requests
echo "$(date) Installing Requests" >> $logFile
/usr/local/bin/python3 -m pip install requests

# Set language to English
echo "$(date) Setting language to en" >> $logFile
languagesetup -langspec en

# Wait for Setup Assistant to finish
while [[ "$(ps aux | grep "Setup Assistant" | grep -v "grep")" != "" ]]; do
	echo "Waiting for Setup Assistant to Terminate" >> $logFile
    sleep 5
done

# Set timezone to mountain time
echo "$(date) Setting Timezone to Mountain Time" >> $logFile
systemsetup -settimezone America/Boise

# Bypass Secure Token
echo "$(date) Bypassing Filevault Screen" >> $logFile
${jamfpolicy} policy -event "bypass-filevault-screen"

# Start Collect Info Python Script
echo "$(date) Starting policy for computer information collection" >> $logFile
${jamfbinary} policy -event "start-collect-computer-info"