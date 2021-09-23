#!/bin/bash
dl_link=$(curl -s https://docs.microsoft.com/en-us/officeupdates/update-history-office-for-mac | grep "Office suite (without Teams)" | head -n 2 | tail -n 1 | awk '{ print $4 }' | sed 's/^.*\(https.*pkg\).*$/\1/')

if ! [ -d "/Library/Application Support/ITCache" ]; then
    mkdir "/Library/Application Support/ITCache"
fi
echo "$(date) Link: $dl_link"
echo "$(date) Starting Download"
curl $dl_link -o "/Library/Application Support/ITCache/office_installer_current_no_teams.pkg" --retry 3 2>&1
echo "$(date) Starting Installation"
/usr/sbin/installer -pkg "/Library/Application Support/ITCache/office_installer_current_no_teams.pkg" -target /Applications 2>&1
rm -rf "/Library/Application Support/ITCache/office_installer_current_no_teams.pkg"
