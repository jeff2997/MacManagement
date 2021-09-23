#!/bin/zsh
url="https://corretto.aws/downloads/latest/amazon-corretto-11-x64-macos-jdk.pkg"
pkgfile="corretto.pkg"
logfile="/Library/Logs/AmazonCorrettoInstallScript.log"
if ! [[ -a "/Library/Application Support/Downloads" ]]; then 
    mkdir "/Library/Application Support/Downloads";
fi
/usr/bin/curl "$url" -o "/Library/Application Support/Downloads/$pkgfile" -L -s

/usr/sbin/installer -pkg "/Library/Application Support/Downloads/${pkgfile}" -target /

rm -f "/Library/Application Support/Downloads/corretto.pkg"