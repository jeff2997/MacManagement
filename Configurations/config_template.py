#!/usr/local/bin/python3

#################################
# Template Configuration
# Rewritten in Python May 2021
# Jeff Pearson
#################################

import os
import subprocess
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime
from os import path
import time

# Variables
# get location of Jamf Binary
proc_get_jamf = subprocess.run(["/usr/bin/which", "jamf"], capture_output=True)
jamf_binary = proc_get_jamf.stdout.decode('ascii').rstrip()
log_file_path = "/var/log/timestamps.log"
error_log_file_path = "/var/log/config_setup_error.log"
config_version = "Template 2021"
dep_notify_cmd_file_path = "/var/tmp/depnotify.log"


# Logging Functions
def log_init():
    log_file = open(log_file_path, 'w')
    dt_current = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log_file.write(dt_current + " Logging Initialized" + '\n')
    log_file.close()
    error_log_file = open(error_log_file_path, 'w')
    dt_current = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    error_log_file.write(dt_current + " Logging Initialized" + '\n')
    error_log_file.close()


def log(log_data):
    log_file = open(log_file_path, 'a')
    dt_current = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log_file.write(dt_current + " " + log_data + '\n')
    log_file.close()
   
   
def log_error(log_data):
    error_log_file = open(error_log_file_path, 'a')
    dt_current = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    error_log_file.write(dt_current + " " + log_data + '\n')
    error_log_file.close()


def log_end():
    log_file = open(log_file_path, 'a')
    dt_current = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log_file.write(dt_current + " Logging Terminated" + '\n')
    log_file.close()
    error_log_file = open(error_log_file_path, 'a')
    dt_current = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    error_log_file.write(dt_current + " Logging Terminated" + '\n')
    error_log_file.close()


# DEPNotify Command Function
def send_command(command):
    dep_notify_cmd_file = open(dep_notify_cmd_file_path, 'a')
    dep_notify_cmd_file.write(command + '\n')
    dep_notify_cmd_file.close()


# Install Function
# Installs programs using jamf policies, then verifies them
# Param: readable_name, install_trigger, install_path(optional), depnotify_string(Human readable)
def install(readable_name, install_trigger, install_path, depnotify_string):
    
    # An installation path was provided
    send_command("Status: " + depnotify_string)
    if install_path != "" and path.exists("/Applications/" + install_path):
        log(readable_name + " is installed correctly")
    else:
        # Start installation
        log(readable_name + " is not installed")
        for retry_attempt in range(1, 5):
            log("Starting installation attempt " + str(retry_attempt))
            if retry_attempt > 1:
                send_command("Status: Installing " + readable_name + " didn't work quite right. Starting attempt " + str(retry_attempt) + "/5")
            
            p = subprocess.Popen(jamf_binary + " policy -event " + install_trigger, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell = True)            
            
            log("---------Start application log---------")
            while p.poll() is None:
                line = p.stdout.readline()
                if not line:
                    break
                log(line.decode().rstrip())
            
            log("---------End application log---------")
            
            if install_path == "":
                log(readable_name + " policy complete. Not verifying.")
                send_command("Status: " + readable_name + " policy has been completed")
                break
            if path.exists("/Applications/" + install_path):
                log(readable_name + " installed correctly")
                send_command("Status: " + readable_name + " policy has been completed")
                break  
        if install_path != "" and not path.exists("/Applications/" + install_path):
            send_command("Status: " + readable_name + " is still not installed after 5 tries. Skipping.")
            log("ERROR: " + readable_name + " is still not installed after 5 attempts")
            log_error("ERROR: " + readable_name + " is still not installed after 5 attempts")


# Cleanup function
# Get rid of splashbuddy and go back to the previous script to restart
def cleanup():
    log("Quitting DEPNotify")
    # send_command("Command: Quit: Configuration Complete!")
    sb_quit_return_code = subprocess.run(["/usr/bin/osascript", "-e", "tell application \"DEPNotify\" to quit"], capture_output=True).returncode
    if sb_quit_return_code == 0:
        log("DEPNotify quit successfully")
        
    log("Deleting DEPNotify")
    subprocess.run(["/bin/rm", "-rf", "/Applications/Utilities/DEPNotify.app"])


# Begin logging
log_init()

# Install DEPNotify
install("DEPNotify", "install-depnotify", "Utilities/DEPNotify.app", "Installing DEPNotify")

#Initialize DEPNotify
subprocess.run(["/bin/rm", "-f", "/var/tmp/depnotify.log"])
subprocess.Popen(["/Applications/Utilities/DEPNotify.app/Contents/MacOS/DEPNotify", "-fullScreen"])
subprocess.run(["/usr/bin/open", "-a", "/Applications/Utilities/DEPNotify.app"])
send_command("Command: Image: /Library/Application Support/StoredImages/Logo.png")
send_command("Command: MainTitle: Computer Configuration in Progress")
send_command("Command: WindowTitle: Computer Configuration")
send_command("Command: KillCommandFile:")
send_command("Command: MainText: This computer is being configured. This could take a while - please don't restart, turn off, or close your computer in the meantime. \\n \\n Selected Configuration: " + config_version)

# Disable sleep mode
send_command("Status: Disabling sleep mode")
subprocess.run(["/usr/bin/pmset", "-a", "sleep", "0"])
subprocess.run(["/usr/bin/pmset", "-a", "hibernatemode", "0"])
subprocess.run(["/usr/bin/pmset", "-a", "disablesleep", "1"])
subprocess.run(["/usr/bin/pmset", "-a", "autopoweroff", "0"])
subprocess.run(["/usr/bin/pmset", "-a", "displaysleep", "0"])

# List of programs to install
# This is the only part that should ever need to change except the config version in the previous line
# -----------------------------------------------------
install("Domain Join", "bind-default", "", "Joining Domain")
install("Adobe Acrobat", "install-AdobeAcrobat2020", "Adobe Acrobat DC/Adobe Acrobat.app", "Installing Adobe Acrobat")
install("Adobe After Effects", "install-AdobeAfterEffects2020", "Adobe After Effects 2020/Adobe After Effects 2020.app", "Installing Adobe After Effects")
install("Adobe Animate", "install-AdobeAnimate2020", "Adobe Animate 2020/Adobe Animate 2020.app", "Installing Adobe Animate")
install("Adobe Audition", "install-AdobeAudition2020", "Adobe Audition 2020/Adobe Audition 2020.app", "Installing Adobe Audition")
install("Adobe Bridge", "install-AdobeBridge2020", "Adobe Bridge 2020/Adobe Bridge 2020.app", "Installing Adobe Bridge")
install("Adobe Character Animator", "install-AdobeCharacterAnimator2020", "Adobe Character Animator 2020/Adobe Character Animator 2020.app", "Installing Adobe Character Animator")
install("Adobe Dimension", "install-AdobeDimension2020", "Adobe Dimension/Adobe Dimension.app", "Installing Adobe Dimension")
install("Adobe InCopy", "install-AdobeInCopy2020", "Adobe InCopy 2020/Adobe InCopy 2020.app", "Installing Adobe InCopy")
install("Adobe InDesign", "install-AdobeInDesign2020", "Adobe InDesign 2020/Adobe InDesign 2020.app", "Installing Adobe InDesign")
install("Adobe Illustrator", "install-AdobeIllustrator2020", "Adobe Illustrator 2020/Adobe Illustrator.app", "Installing Adobe Illustrator")
install("Adobe Lightroom", "install-AdobeLightroom2020", "Adobe Lightroom CC/Adobe Lightroom.app", "Installing Adobe Lightroom")
install("Adobe Lightroom Classic", "install-AdobeLightroomClassic2020", "Adobe Lightroom Classic/Adobe Lightroom Classic.app", "Installing Adobe Lightroom Classic")
install("Adobe Media Encoder", "install-AdobeMediaEncoder2020", "Adobe Media Encoder 2020/Adobe Media Encoder 2020.app", "Installing Adobe Media Encoder")
install("Adobe Photoshop", "install-AdobePhotoshop2020", "Adobe Photoshop 2020/Adobe Photoshop 2020.app", "Installing Adobe Photoshop")
install("Adobe Prelude", "install-AdobePrelude2020", "Adobe Prelude 2020/Adobe Prelude 2020.app", "Installing Adobe Prelude")
install("Adobe Premiere Pro", "install-AdobePremierePro2020", "Adobe Premiere Pro 2020/Adobe Premiere Pro 2020.app", "Installing Adobe Premiere Pro")
install("Adobe XD", "install-AdobeXD2020", "Adobe XD/Adobe XD.app", "Installing Adobe XD")
install("Microsoft Office", "install-office", "Microsoft Word.app", "Installing Microsoft Office")
install("License Office", "install-MSOfficeSerial", "", "Licensing Microsoft Office")
install("Keynote", "install-keynote", "Keynote.app", "Installing Keynote")
install("Numbers", "install-numbers", "Numbers.app", "Installing Numbers")
install("Pages", "install-pages", "Pages.app", "Installing Pages")
install("Chrome", "install-chrome", "Google Chrome.app", "Installing Google Chrome")
install("Firefox", "install-firefox", "Firefox.app", "Installing Firefox")
install("Printer Drivers", "install-print", "", "Adding Printer Drivers")
install("Amazon Corretto", "install-java", "", "Installing Amazon Corretto (Java)")
install("VLC", "install-vlc", "VLC.app", "Installing VLC")
install("Sophos", "install-sophos", "Sophos/Sophos Endpoint.app", "Installing Sophos")
install("Zoom", "install-zoom", "zoom.us.app", "Installing Zoom")
install("Background", "drop-bg", "", "Dropping Desktop Background")

# -----------------------------------------------------
send_command("Status: Re-enabling sleep mode")
subprocess.run(["/usr/bin/open", "-a", "/Applications/Utilities/DEPNotify.app"])
subprocess.run(["/usr/bin/pmset", "-a", "sleep", "1"])
subprocess.run(["/usr/bin/pmset", "-a", "hibernatemode", "3"])
subprocess.run(["/usr/bin/pmset", "-a", "disablesleep", "0"])
subprocess.run(["/usr/bin/pmset", "-a", "autopoweroff", "1"])
subprocess.run(["/usr/bin/pmset", "-a", "displaysleep", "10"])
send_command("Status: Configuration Complete! Restarting...")
time.sleep(3) # Give a couple seconds to read the message

# End logging and cleanup
log_end()
cleanup()