#!/bin/bash
# Modified by Jeff Pearson to support arm64 macs. 
# Based on original script by Jon Farage
# This could use some cleanup

dmgfile="googlechrome.dmg"
volname="Google Chrome"
logfile="/Library/Logs/GoogleChromeInstallScript.log"

url='https://dl.google.com/chrome/mac/stable/GGRO/googlechrome.dmg'
universal_url='https://dl.google.com/chrome/mac/universal/stable/GGRO/googlechrome.dmg'

if [ "$(/usr/bin/uname -p)" = "x86_64" -o "$(/usr/bin/uname -p)" = "i386" ]; then
    /bin/echo "--" >> ${logfile}
    /bin/echo "x86 Architecture Selected" >> ${logfile}
    /bin/echo "`date`: Downloading latest version." >> ${logfile}
    /usr/bin/curl -s -o /tmp/${dmgfile} ${url}
    /bin/echo "`date`: Mounting installer disk image." >> ${logfile}
    /usr/bin/hdiutil attach /tmp/${dmgfile} -nobrowse -quiet
    /bin/echo "`date`: Installing..." >> ${logfile}
    ditto -rsrc "/Volumes/${volname}/Google Chrome.app" "/Applications/Google Chrome.app"
    /bin/sleep 10
    /bin/echo "`date`: Unmounting installer disk image." >> ${logfile}
    /usr/bin/hdiutil detach $(/bin/df | /usr/bin/grep "${volname}" | awk '{print $1}') -quiet
    /bin/sleep 10
    /bin/echo "`date`: Deleting disk image." >> ${logfile}
    /bin/rm /tmp/"${dmgfile}"
elif [ "$(/usr/bin/uname -p)" = "arm" ]; then
    /bin/echo "--" >> ${logfile}
    /bin/echo "ARM Architecture Selected" >> ${logfile}
    /bin/echo "`date`: Downloading latest version." >> ${logfile}
    /usr/bin/curl -s -o /tmp/${dmgfile} ${universal_url}
    /bin/echo "`date`: Mounting installer disk image." >> ${logfile}
    /usr/bin/hdiutil attach /tmp/${dmgfile} -nobrowse -quiet
    /bin/echo "`date`: Installing..." >> ${logfile}
    ditto -rsrc "/Volumes/${volname}/Google Chrome.app" "/Applications/Google Chrome.app"
    /bin/sleep 10
    /bin/echo "`date`: Unmounting installer disk image." >> ${logfile}
    /usr/bin/hdiutil detach $(/bin/df | /usr/bin/grep "${volname}" | awk '{print $1}') -quiet
    /bin/sleep 10
    /bin/echo "`date`: Deleting disk image." >> ${logfile}
    /bin/rm /tmp/"${dmgfile}"
else
    /bin/echo "--" >> ${logfile}
    /bin/echo "Neither Architecture Detected" >> ${logfile}
    exit 1
fi
exit 0