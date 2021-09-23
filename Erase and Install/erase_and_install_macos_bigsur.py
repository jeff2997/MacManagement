#!/usr/local/bin/python3

#######################################
# Erases and updates the OS
# September 2021
# Default log location: /var/log/destroy.log
#######################################

# Imports
import sys
import requests
import json
import subprocess
import socket
import platform
from datetime import datetime


# Variables
api_username = "apiUser"
api_password = ""
salt = ""
passphrase = ""
encrypted_string = sys.argv[4] # Parameter 4 from Jamf
log_file_path="/var/log/destroy.log"
# url="http://swcdn.apple.com/content/downloads/49/54/071-71342-A_TOSWTG0P9A/0pl87hjdasybzmpr2liwamgm9pmmorqmzh/InstallAssistant.pkg" # 11.5.1
url="http://swcdn.apple.com/content/downloads/57/38/071-97382-A_OEKYSXCO6D/97vrhncortwd3i38zfogcscagmpwksdzce/InstallAssistant.pkg" # 11.6
jss_api_password_url = "https://jss.yourorganization.com:8443/JSSResource/computers/name/"






# decrypt_string() based on Jamf's
# https://github.com/jamf/Encrypted-Script-Parameters/blob/master/EncryptedStrings_Python.py
def decrypt_string(input_string, salt, passphrase):
    '''Usage: >>> DecryptString("Encrypted String", "Salt", "Passphrase")'''
    decrypted = subprocess.run(['/usr/bin/openssl', 'enc', '-aes256', '-d', '-a', '-A', '-S', salt, '-k', passphrase], input=input_string, encoding='ascii', capture_output=True)
    return decrypted.stdout.rstrip()

# get_password()
# accepts a computer name and gets the admin password from the server
def get_password(name, username, password):
    headers = {'accept': 'application/json'}
    url=jss_api_password_url + name
    response = requests.get(url, auth=(username, password), headers=headers)
    if response.status_code == 200:
        data = json.loads(response.text)
        extension_attributes = data["computer"]["extension_attributes"]
        for attribute in extension_attributes:
            if attribute["name"] == "Local Admin Password":
                if attribute["value"] != "":
                    return attribute["value"] # This is the password
        return None # If there is no password found, return None
    else:
        return None

# Logging Function
def log(log_data):
    log_file = open(log_file_path, 'a')
    dt_current = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log_file.write(dt_current + " " + log_data + '\n')
    log_file.close()



#-----------------------------------------------------------------
# Start Download, erase old installers to ensure up-to-date
#-----------------------------------------------------------------

# Uncomment to delete an old version of the installer first

#log("Prepping and cleaning up before download")
#if not os.path.exists('/tmp/download'):
#    os.mkdir('/tmp/download')
#if os.path.exists('/tmp/download/InstallAssistant.pkg'):
#    os.remove('/tmp/download/InstallAssistant.pkg')
#if os.path.exists('/Applications/Install macOS Big Sur.app'):
#	shutil.rmtree('/Applications/Install macOS Big Sur.app', ignore_errors=True)

log("Starting download")
subprocess.run(["/usr/sbin/softwareupdate", "--fetch-full-installer"])

# Uncomment to download from the internet

# urllib.request.urlretrieve(url, '/tmp/download/InstallAssistant.pkg')
# subprocess.run(['/usr/sbin/installer', '-pkg', '/tmp/download/InstallAssistant.pkg', '-target', '/'])


#-----------------------------------------------------------------
# Start Installer
#-----------------------------------------------------------------

log("Download complete! Starting pkg install")
architecture = platform.uname().machine
if architecture == "arm64":
    log("Apple silicon computer detected")
    #We are Apple Silicon
    # Get Password for local admin user
    api_password = decrypt_string(encrypted_string, salt, passphrase)
    computer_password = get_password(socket.gethostname(), api_username, api_password)
    computer_username="localadminuser"
    log("Username: " + computer_username)
    log("Computer password: " + computer_password)
    file = open("/tmp/erase.sh", "w")
    file.write("#!/bin/bash\n")
    file.write("echo \"" + computer_password + "\" | \"/Applications/Install macOS Big Sur.app/Contents/Resources/startosinstall\" --eraseinstall --forcequitapps --agreetolicense --newvolumename \"Macintosh HD\" --user " + computer_username + " --stdinpass &> \"/var/log/destroy.log\" &\n")
    file.close()
    p = subprocess.Popen(['/bin/bash', '/tmp/erase.sh'])
    print("Installation started - see destroy.log for details")
else:
    log("Intel computer detected")
    # Intel
    file = open("/tmp/erase.sh", "w")
    file.write("#!/bin/bash\n")
    file.write("\"/Applications/Install macOS Big Sur.app/Contents/Resources/startosinstall\" --eraseinstall --forcequitapps --agreetolicense --newvolumename \"Macintosh HD\" &> \"/var/log/destroy.log\" &\n")
    file.close()
    p = subprocess.Popen(['/bin/bash', '/tmp/erase.sh'])
    print("Installation started - see destroy.log for details")