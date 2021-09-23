#!/usr/local/bin/python3

#################################
# Your Organization's Initial Enrollment Script
# Last Edited September 2021
# Created by Jeff Pearson
# This script is an advanced way to collect information from the end user.
# It contains several forms of error checking, and is easily extensible
# To point to several different MDM policies that also run scripts which
# can do things like install pre-determined sets of software
#################################

# Imports
import os
import subprocess
import PySimpleGUI as sg
import re
from datetime import datetime, date


# DEVELOPMENT TOOLS
development_mode = False

# Variables
asset_tag = ""
computer_name = ""
use_type = ""
username = ""
asset_tag_template = re.compile('^[0-9]{6}$') # For a 6 digit asset tag
available_uses = ["Use 1", "Use 2", "Use 3", "Use 4", "Use 5", "Use 6"]
log_file_path = "/var/log/select_config.log"
processFile = "/var/log/processes.log"
config = ""
max_length = 15
logo_path = "/Library/Application Support/LogoConfig/Logo_Small.png"


# get location of Jamf Binary
proc_get_jamf = subprocess.run(["/usr/bin/which", "jamf"], capture_output=True)
jamf_binary = proc_get_jamf.stdout.decode('ascii').rstrip()

# Lab Room Variables
# Each of these is an array that contains part of a name. For example, if you have a lab
# called LABJOE, and the computers are named LABJOE1, LABJOE2, etc. Then you could have a 
# variable called LABJOE that contains LABJOE. You would then edit the rest of the script
# (You can use find and replace) to use that set of naming conventions. That array would then
# affect all computers with LABJOE in the name. Note that computer names are set to all-caps
# automatically.
LAB1 = ['LAB1']
LAB2 = ['LAB2']
LAB3 = ['LAB3']
LAB4 = ['LAB4']
LAB5 = ['LAB5']
LAB6 = ['LAB6']
LAB7 = ['LAB7']
LAB8 = ['LAB8']
LAB9 = ['LAB9']
LAB10 = ['LAB10', 'NAME1']

# Advanced Tools
CONFIGS = ['LAB1', 'LAB2', 'LAB3', 'LAB4', 'LAB5', 'LAB6', 'LAB7', 'LAB8', 'LAB9', 'LAB10']
selected_config = None

# Creates a log file and clears it if it is already there. 
def log_init():
    log_file = open(log_file_path, 'w')
    dt_current = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log_file.write(dt_current + " Logging Initialized" + '\n')
    log_file.close()

# Appends to the log file, and adds timestamps automatically
def log(log_data):
    log_file = open(log_file_path, 'a')
    dt_current = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log_file.write(dt_current + " " + log_data + '\n')
    log_file.close()

# Simply prints that the logging is terminated. 
# Designed to run once at the end of the script
def log_end():
    log_file = open(log_file_path, 'a')
    dt_current = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    log_file.write(dt_current + " Logging Terminated" + '\n')
    log_file.close()

# Returns the configuration that is supposed to take effect
# based upon the computer name passed to it
def get_config(computer_name):
    # Still need to get first 5 or 6 of computer name
    if any(name in computer_name for name in LAB1):
        return "LAB1"
    elif any(name in computer_name for name in LAB4):
        return "LAB4"
    elif any(name in computer_name for name in LAB2):
        return "LAB2"
    elif any(name in computer_name for name in LAB3):
        return "LAB3"
    elif any(name in computer_name for name in LAB5):
        return "LAB5"
    elif any(name in computer_name for name in LAB6):
        return "LAB6"
    elif any(name in computer_name for name in LAB7):
        return "LAB7"
    elif any(name in computer_name for name in LAB8):
        return "LAB8"
    elif any(name in computer_name for name in LAB10):
        return "LAB10"
    elif any(name in computer_name for name in LAB9):
        return "LAB9"
    else:
        return "LAB11"

# Prevent computer from sleeping
caffeinate_process = subprocess.Popen("exec " + "/usr/bin/caffeinate", stdout=subprocess.PIPE, 
                       shell=True)


# Creates the main info collection window
# Also calls all other functions
# which can verify information and upload it.
def main():
    # Draw Information Collection Window
    sg.theme('LightGrey1')

    logo = [[sg.Image(logo_path)]]
    left_text = [[sg.Text('Computer Name: ', font=('Helvetica 16'))],
                [sg.Text('Asset Tag: ', font=('Helvetica 16'))],
                [sg.Text('Computer Use Type: ', font=('Helvetica 16'))],
                [sg.Text("End User\'s Username:", font=('Helvetica 16'), key="UTEXT")]]

    input_fields = [[sg.InputText(key="CNAME", size=(50,1), tooltip='The name of the computer (less than 15 characters)', font=('Helvetica 16'))],
                    [sg.InputText( key="TAG", size=(50,1), tooltip='The 6 digit asset tag', font=('Helvetica 16'))],
                    [sg.Combo(available_uses, key="USE", size=(50,1), tooltip='What is this computer for?', font=('Helvetica 16'), readonly=True, enable_events=True)],
                    [sg.InputText( key="USERNAME", size=(50,1), tooltip='Username of the person that is receiving it (if applicable)', font=('Helvetica 16'))]]

    buttons = [[sg.Button("Naming Help", key="NAME_HELP", size=(20,1)), sg.Button("Ok", size=(20,1))]]

    layout = [  [sg.Col(logo, vertical_alignment='center', justification='center')],
                [sg.Col(left_text), sg.Column(input_fields)],
                [sg.Col(buttons, vertical_alignment='center', justification='center')]]

    # Create the Window
    window = sg.Window('Your Organization Computer Configuration', layout, finalize=True)

    # Event Loop to process "events" and get the "values" of the inputs
    my_popup = ''
    draw_win = True
    window["UTEXT"].update(visible=False) # Hiding these now puts white space in there so it doesn't awkwardly resize
    window["USERNAME"].update(visible=False)

    while True:
        # if(my_popup != 'OK'):
        event, values = window.read()
        
        if values != None:
            computer_name = values['CNAME']
            asset_tag = values['TAG']
            use_type = values['USE']
            username = values['USERNAME']

        if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
            if not development_mode:
                sg.popup("Configuration has been cancelled. Please re-image this machine", title="Error")
                exit(1)
            else:
                exit(0)

        if event == "USE":
            if (values['USE'] == "Use 1" or values['USE'] == "Use 4"):
                # Then we can show the Use 1 or Use 4 name field
                window["UTEXT"].update(visible=True)
                window["USERNAME"].update(visible=True)
            else:
                window["UTEXT"].update(visible=False)
                window["USERNAME"].update(visible=False)

        # Verify that collected information is valid
        if event == "Ok":
            if len(computer_name) == 0:
                sg.popup("Please enter a computer name", title="Error")
            elif len(computer_name) > 15:
                sg.popup("Computer names should not be longer than 15 characters")
            elif not asset_tag_template.match(asset_tag):
                sg.popup("Asset tags must only contain 6 numbers", title="Error")
            elif use_type not in available_uses:
                sg.popup("Please select a valid computer use type", title="Error")
            elif use_type == "Use 1" and username == "":
                sg.popup("Please enter a valid username", title="Error") 
            else:
                if (use_type != "Use 1" and use_type != "Use 4") and username != "":
                    username = ""
                new_cn = check_name_for_errors(computer_name, asset_tag, use_type)
                if new_cn != False:
                    computer_name = new_cn
                    if not development_mode: log("Correcting case of username and computer name")
                    if username != "":
                        username = username.lower()
                    window["CNAME"].update(computer_name)
                computer_name = computer_name.upper()
                config = get_config(computer_name)
                # new_config = config
                if len(computer_name) > 15:
                    sg.popup("Computer names should not be longer than 15 characters")
                else:
                    # my_popup = sg.PopupOKCancel("This will deploy the " + config + " configuration. Is that right?", title="Confirm Config Selection")
                    verified = verify_config(config, computer_name, asset_tag, use_type, username)
                    # config = new_config
                    if verified == True:
                        window.hide()
                        break
        if event == "NAME_HELP":
            help()

    
    if not development_mode: 
        # Start Logging
        log_init()

        # Save all information to Jamf
        if username != "":
            log("Username: " + username)
        log("Asset Tag: " + asset_tag)
        log("Computer Name: " + computer_name)

        log("Saving asset tag to Jamf")
        subprocess.run([jamf_binary, "recon", "-assetTag", asset_tag])

        if username != "":
            log("Saving username to Jamf")
            subprocess.run([jamf_binary, "recon", "-endUsername", username])

        log("Saving computer name locally")
        subprocess.run(['/usr/sbin/scutil', '--set', 'ComputerName', computer_name])
        subprocess.run(['/usr/sbin/scutil', '--set', 'LocalHostName', computer_name])
        subprocess.run(['/usr/sbin/scutil', '--set', 'HostName', computer_name])

        log("Verifying computer name saved correctly")
        saved_cn = subprocess.run(['/usr/sbin/scutil', '--get', 'ComputerName'], capture_output=True).stdout.decode('ascii').rstrip()
        saved_lhn = subprocess.run(['/usr/sbin/scutil', '--get', 'LocalHostName'], capture_output=True).stdout.decode('ascii').rstrip()
        saved_hn = subprocess.run(['/usr/sbin/scutil', '--get', 'HostName'], capture_output=True).stdout.decode('ascii').rstrip()

        if saved_cn != computer_name:
            log("Error saving computer name to ComputerName attribute")

        if saved_lhn != computer_name:
            log("Error saving computer name to LocalHostName attribute")

        if saved_hn != computer_name:
            log("Error saving computer name to HostName attribute")

            
            
        log("Computer name verification complete, saving to server...")

        p = subprocess.run([jamf_binary, 'recon'])
                        
        if p.returncode != 0:
            log("Failed to save computer name to server")
        else:
            log("CN saved successfully!")


        # Start Image Process
        if config == "LAB1":
            log("Starting LAB1, 114D, 53, 65, 67 Configuration")
            subprocess.run([jamf_binary, 'policy', '-event', 'config-LAB1'])
        elif config == "LAB2":
            log("Starting LAB2 Configuration")
            subprocess.run([jamf_binary, 'policy', '-event', 'config-LAB2'])
        elif config == "LAB3":
            log("Starting LAB3 Configuration")
            subprocess.run([jamf_binary, 'policy', '-event', 'config-LAB3'])
        elif config == "LAB4":
            log("Starting LAB4 Configuration")
            subprocess.run([jamf_binary, 'policy', '-event', 'config-LAB4'])
        elif config == "LAB5":
            log("Starting LAB5 Configuration")
            subprocess.run([jamf_binary, 'policy', '-event', 'config-LAB5'])
        elif config == "LAB6":
            log("Starting LAB6 Configuration")
            subprocess.run([jamf_binary, 'policy', '-event', 'config-LAB6'])
        elif config == "LAB7":
            log("Starting LAB7 Configuration")
            subprocess.run([jamf_binary, 'policy', '-event', 'config-LAB7'])
        elif config == "LAB8":
            log("Starting LAB8 Configuration")
            subprocess.run([jamf_binary, 'policy', '-event', 'config-LAB8'])
        elif config == "LAB9":
            log("Starting LAB9 Configuration")
            subprocess.run([jamf_binary, 'policy', '-event', 'config-LAB9'])
        elif config == "LAB10":
            log("Starting LAB10 Configuration")
            subprocess.run([jamf_binary, 'policy', '-event', 'config-LAB10'])
        else:
            log("Starting LAB11 Configuration")
            subprocess.run([jamf_binary, 'policy', '-event', 'config-LAB11'])

        # Clean up after processes finish
        log("Killing Caffeinate")
        caffeinate_process.kill()
        log("Restarting Computer")
        log_end()
        os.system("reboot")
    else:
        # This is a development environment
        print("DEVELOPMENT MODE")
        print("Username: " + username)
        print("Asset tag: " + asset_tag)
        print("Computer Name: " + computer_name)
        print("Config: " + config)



# Displays a window that offers help with the computer naming conventions.
def help():
    # Draw Help Window
    sg.theme('LightGrey1')
    title_font = ("Helvetica", 16, "bold")
    font = ("Helvetica", 16)
    size=(40,1)
    
    title = [   [sg.Text("Naming Convention Reference Guide", font=title_font, justification='center')],
                [sg.Text("Select a configuration below for more information", font=("Helvetica", 12))]]

    configurations = [  [sg.Text("Lab", font=font)],
                        [sg.Button("Lab Room Numbers", key="LAB1", size=size, font=font)],
                        [sg.Button("Lab", key="LAB2", size=size, font=font)],
                        [sg.Button("Lab Room Numbers", key="LAB3", size=size, font=font)],
                        [sg.Text("Lab", font=font)],
                        [sg.Button("Lab Room Numbers", key="LAB4", font=font, size=size)],
                        [sg.Text("Lab", font=font)],
                        [sg.Button("Lab Room Numbers", key="LAB5", font=font, size=size)],
                        [sg.Text("Lab", font=font)],
                        [sg.Button("Lab Room Numbers", key="LAB6", font=font, size=size)],
                        [sg.Text("Lab", font=font)],
                        [sg.Button("Lab Room Numbers", key="LAB7", size=size, font=font)],
                        [sg.Button("Lab", key="LAB8", size=size, font=font)],
                        [sg.Text("Lab Room Numbers", font=font)],
                        [sg.Button("Lab", key="LAB9", size=size, font=font)],
                        [sg.Button("Lab", key="LAB10", size=size, font=font)],
                        [sg.Button("Lab", key="LAB11", size=size, font=font)]]

    layout = [  [sg.Col(title, vertical_alignment='center', justification='center')],
                [sg.Col(configurations, vertical_alignment='center', justification='left')]]
    # Create the Window
    window = sg.Window('Naming Convention Reference Guide', layout, finalize=True)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
            window.close()
            break

        elif event == "LAB1":
            info("Lab and Related Rooms",
                "Two Digit Year, Three Digit Building Code, Three Digit Room Number, L, Two Digit Computer Number",
                "Example Computer Name - Installed in 2021, in Lab 1, computer number 01\nSecond Example here",
                "Lab")
        elif event == "LAB2":
            info("Lab and Related Rooms",
                "Two Digit Year, Three Digit Building Code, Three Digit Room Number, L, Two Digit Computer Number",
                "Example Computer Name - Installed in 2021, in Lab 1, computer number 01\nSecond Example here",
                "Lab")
        elif event == "LAB3":
            info("Lab and Related Rooms",
                "Two Digit Year, Three Digit Building Code, Three Digit Room Number, L, Two Digit Computer Number",
                "Example Computer Name - Installed in 2021, in Lab 1, computer number 01\nSecond Example here",
                "Lab")
        elif event == "LAB4":
            info("Lab and Related Rooms",
                "Two Digit Year, Three Digit Building Code, Three Digit Room Number, L, Two Digit Computer Number",
                "Example Computer Name - Installed in 2021, in Lab 1, computer number 01\nSecond Example here",
                "Lab")
        elif event == "LAB5":
            info("Lab and Related Rooms",
                "Two Digit Year, Three Digit Building Code, Three Digit Room Number, L, Two Digit Computer Number",
                "Example Computer Name - Installed in 2021, in Lab 1, computer number 01\nSecond Example here",
                "Lab")
        elif event == "LAB6":
            info("Lab and Related Rooms",
                "Two Digit Year, Three Digit Building Code, Three Digit Room Number, L, Two Digit Computer Number",
                "Example Computer Name - Installed in 2021, in Lab 1, computer number 01\nSecond Example here",
                "Lab")
        elif event == "LAB7":
            info("Lab and Related Rooms",
                "Two Digit Year, Three Digit Building Code, Three Digit Room Number, L, Two Digit Computer Number",
                "Example Computer Name - Installed in 2021, in Lab 1, computer number 01\nSecond Example here",
                "Lab")
        elif event == "LAB8":
            info("Lab and Related Rooms",
                "Two Digit Year, Three Digit Building Code, Three Digit Room Number, L, Two Digit Computer Number",
                "Example Computer Name - Installed in 2021, in Lab 1, computer number 01\nSecond Example here",
                "Lab")
        elif event == "LAB9":
            info("Lab and Related Rooms",
                "Two Digit Year, Three Digit Building Code, Three Digit Room Number, L, Two Digit Computer Number",
                "Example Computer Name - Installed in 2021, in Lab 1, computer number 01\nSecond Example here",
                "Lab")
        elif event == "LAB10":
            info("Lab and Related Rooms",
                "Two Digit Year, Three Digit Building Code, Three Digit Room Number, L, Two Digit Computer Number",
                "Example Computer Name - Installed in 2021, in Lab 1, computer number 01\nSecond Example here",
                "Lab")
        elif event == "LAB11":
            info("Lab and Related Rooms",
                "Two Digit Year, Three Digit Building Code, Three Digit Room Number, L, Two Digit Computer Number",
                "Example Computer Name - Installed in 2021, in Lab 1, computer number 01\nSecond Example here",
                "Lab")



# Displays some information to the user - designed to display 
# config/naming info from the help screen
def info(window_title, naming_convention, name_examples, room_numbers=None):
    sg.theme('LightGrey1')
    title_font = ("Helvetica", 16, "bold")
    font = ("Helvetica", 16)
    size=(40,1)

    if room_numbers != None:
        layout = [  [sg.Text(window_title, justification='center', font=("Helvetica", 20, "bold"))],
                    [sg.Text("Naming Convention: ", font=title_font)],
                    [sg.Text(naming_convention, font=font)],
                    [sg.Text("Valid Name Example(s): ", font=title_font)],
                    [sg.Text(name_examples, font=font)],
                    [sg.Text("Applicable Room Numbers: ", font=title_font)],
                    [sg.Text(room_numbers, font=font)],
                    [sg.Col([[sg.Button("OK", key='OK', size=(10,1))]], justification='center', vertical_alignment='center')]]
    else:
        layout = [  [sg.Text(window_title, justification='center', font=("Helvetica", 20, "bold"))],
                    [sg.Text("Naming Convention: ", font=title_font)],
                    [sg.Text(naming_convention, font=font)],
                    [sg.Text("Valid Name Example(s): ", font=title_font)],
                    [sg.Text(name_examples, font=font)],
                    [sg.Col([[sg.Button("OK", key='OK', size=(10,1))]], justification='center', vertical_alignment='center')]]

    window = sg.Window(window_title, layout, finalize=True)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "OK": # if user closes window or clicks OK
            window.close()
            break



# Returns a computer name that it collects from the user
# Also displays an error message to the user (passed as a parameter)
# so that they know approximately what they have to fix
# Also takes a suggested name, which is generated and assumed
# not to have any problems.
def name_query(error, name, suggested_name):
    sg.theme('LightGrey1')
    title_font = ("Helvetica", 16, "bold")
    font = ("Helvetica", 16)
    # size=(40,1)
    text_stuff = [  [sg.Text("Oh no! Your computer name might have an error :/", justification='center', font=("Helvetica", 20, "bold"))],
                    [sg.Text(error + " You can fix it right here.", font=title_font)],
                    [sg.Text("You provided this: " + name, font=font)],
                    [sg.Text("Did you mean: ", font=font ), sg.InputText(suggested_name, font=font, key="NAME")]]
    
    buttons = [[sg.Button("Accept Changes", key='YES', size=(25,1)), sg.Button("Continue Without Changing", key='NO', size=(25,1)), sg.Button("Naming Help", key="HELP", size=(25,1))]]

    layout = [  [sg.Col(text_stuff, justification='center', vertical_alignment='center')],
                [sg.Col(buttons, justification='center', vertical_alignment='center')]]


    window = sg.Window("Computer Name Automatic Resolution Assistant", layout, finalize=True)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
            window.close()
            return False
        elif event == "YES":
            if len(values["NAME"]) > max_length:
                sg.popup("Computer names should not be longer than 15 characters")
            else:
                window.close()
                return values["NAME"]
        elif event == "NO":
            window.close()
            return name # To retain the old one
            
        elif event ==  "HELP":
            help()

def name_error(name):
    sg.theme('LightGrey1')
    title_font = ("Helvetica", 16, "bold")
    font = ("Helvetica", 16)
    # size=(40,1)
    title_stuff = [ [sg.Text("Oh no! Your computer name might contain an error :/", font=("Helvetica", 20, "bold"), size=(50,2))]]
    help_stuff = [  [sg.Text("If you require assistance, feel free to review the Naming Guidelines --->", font=font), sg.Button("Naming Guidelines", key="HELP", font=font)]]
    body_stuff = [  [sg.Text("Please double check the Computer Name, make any necessary changes, and click OK when done: ", font=font ), sg.InputText(name, font=font, key="NAME")]]
    
    buttons = [[sg.Button("OK", key='YES', size=(10,1))]]

    layout = [  [sg.Col(title_stuff, justification='center', vertical_alignment='center')],
                [sg.Col(help_stuff, justification='center', vertical_alignment='center')],
                [sg.Col(body_stuff, justification='center', vertical_alignment='center')],
                [sg.Col(buttons, justification='center', vertical_alignment='center')]]


    window = sg.Window("Computer Name Automatic Resolution Assistant", layout, finalize=True)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
            window.close()
            return False
        elif event == "YES":
            
            if len(values["NAME"]) > max_length:
                sg.popup("Computer names should not be longer than 15 characters")
            else:
                window.close()
                return values["NAME"]
            return values["NAME"]
        elif event == "HELP":
            help()


# Returns False if no errors found, or if user overrides
# Returns a new computer name suggestion if the user provides one
# This will need to be heavily edited to provide your desired functionality
def check_name_for_errors(computer_name, asset_tag, computer_use_type):
    max_name_length = 15
    example_pattern_1 = re.compile('^[0-9]{2}[a-zA-Z]{3}[0-9]{3}[a-zA-Z]{0,1}[LlCc][0-9]{2}$')
    example_pattern_2 = re.compile('^[0-9]{2}[a-zA-Z]{3}[0-9]{3}[a-zA-Z]{0,1}-[0-9]{6}$')
    example_pattern_3 = re.compile('^[0-9]{2}[A-Z][a-zA-Z]{2,}$')
    if computer_use_type == "Use 1":
        if development_mode: print("Use 1 Name Checker")
        match_result = re.match(example_pattern_3, computer_name)
        if match_result: # If it matches, then we're good.
            return False
        else:
            # Try and guess what happened.
            no_year = re.compile('^[A-Z][a-zA-Z]{2,}$') # It looks like you forgot to add a year. Did you mean __?
            one_digit_year = re.compile('^[0-9][A-Z][a-zA-Z]{2,}$') # It looks like you forgot to use a two-digit year. Did you mean?
            no_year_match = re.match(no_year, computer_name)
            one_digit_year_match = re.match(one_digit_year, computer_name)
            if no_year_match:
                print("Here:")
                year_code = str(date.today().year)[-2:]
                new_cn = year_code + computer_name
                if len(new_cn) >  max_name_length:
                    new_cn = new_cn[:max_name_length]
                cn_query = name_query("You might have forgotten the date code.", computer_name, new_cn)
                if cn_query == computer_name:
                    return False
                else:
                    return cn_query
            elif one_digit_year_match:
                tens_digit = str(date.today().year)[-2:-1]
                ones_digit = computer_name[:1]
                year_code = int(tens_digit + ones_digit)
                current_year_code = str(date.today().year)[-2:]
                if int(year_code) > int(current_year_code):
                    year_code += 100
                    year_code -= 10
                    year_code = str(year_code)
                    if len(year_code) > 2:
                        year_code = year_code[-2:]
                tens_digit = year_code[:-1]
                
                new_cn = tens_digit + computer_name
                if len(new_cn) >  max_name_length:
                    new_cn = new_cn[:max_name_length]
                cn_query = name_query("You might have used a one-digit year. Two digit years are now standard.", computer_name, new_cn)
                if cn_query == computer_name:
                    return False
                else:
                    return cn_query
            else:
                new_cn = name_error(computer_name)
                if new_cn == computer_name:
                    return False
                else:
                    return new_cn

    elif computer_use_type == "Use 2" or computer_use_type == "Use 3" or computer_use_type == "Use 4":
        if not "-" in computer_name:
            if len(computer_name) > max_name_length - 7:
                cn_query = computer_name[:max_name_length - 7] # make it the right length to fit - and an asset tag
            else:
                cn_query = computer_name
            cn_query = cn_query + "-" + asset_tag
            cn_query = name_query("You might have forgotten the asset tag", computer_name, cn_query)
            if cn_query == computer_name:
                return False
            else:
                return cn_query
        else:
            match_result = re.match(example_pattern_2, computer_name)
            asset_tag_from_name = computer_name.split("-")[1]

            if match_result and (asset_tag_from_name == asset_tag): # If it matches, then we're good.
                return False
            else:
                bad_asset_tag = re.compile('^[0-9]{2}[a-zA-Z]{3}[0-9]{3}[a-zA-Z]{0,1}-[0-9]{1,5}$')
                bad_asset_tag_2 = re.compile('^[0-9]{2}[a-zA-Z]{3}[0-9]{3}[a-zA-Z]{0,1}-[0-9]{7,}$')
                no_year = re.compile('^[a-zA-Z]{3}[0-9]{3}[a-zA-Z]{0,1}-[0-9]{6}$')
                bad_asset_tag_match = re.match(bad_asset_tag, computer_name)
                bad_asset_tag_2_match = re.match(bad_asset_tag_2, computer_name)
                no_year_match = re.match(no_year, computer_name)

                if no_year_match:
                    year_code = str(date.today().year)[-2:]
                    new_cn = year_code + computer_name
                    if len(new_cn) >  max_name_length:
                        new_cn = new_cn[:max_name_length]
                    cn_query = name_query("You might have forgotten the date code.", computer_name, new_cn)
                    if cn_query == computer_name:
                        return False
                    else:
                        return cn_query
                elif bad_asset_tag_match or bad_asset_tag_2_match:
                    asset_tag_from_name = computer_name.split("-")[1]
                    name_no_asset_tag = computer_name.split("-")[0] + "-"
                    new_cn = name_no_asset_tag + asset_tag
                    cn_query = name_query("It looks like there's an issue with your asset tag.", computer_name, new_cn)
                    if cn_query == computer_name:
                        return False
                    else:
                        return cn_query
                elif asset_tag_from_name != asset_tag:
                    new_cn = computer_name.split("-")[0] + "-" + asset_tag
                    cn_query = name_query("It looks like your asset tags don't match.", computer_name, new_cn)
                    if cn_query == computer_name:
                        return False
                    else:
                        return cn_query
                else:
                    new_cn = name_error(computer_name)
                    if new_cn == computer_name:
                        return False
                    else:
                        return new_cn

    elif computer_use_type == "Use 5":
        # print("Use 5")
        match_result = re.match(example_pattern_1, computer_name)
        if match_result: # If it matches, then we're good.
            return False
        else: #Let's figure out why it didn't match. Hopefully.
            no_year = re.compile('^[a-zA-Z]{3}[0-9]{3}[a-zA-Z]{0,1}[LlCc][0-9]{2}$')
            no_year_dash = re.compile('^[a-zA-Z]{3}[0-9]{3}[a-zA-Z]{0,1}-[0-9]{2}$')
            dash = ("^[0-9]{2}[a-zA-Z]{3}[0-9]{3}[a-zA-Z]{0,1}[LlCc][0-9]{2}$")
            no_year_match = re.match(no_year, computer_name)
            no_year_dash_match = re.match(no_year_dash, computer_name)
            dash_match = re.match(dash, computer_name)

            if no_year_match:
                print("Missing a year")
                year_code = str(date.today().year)[-2:]
                new_cn = year_code + computer_name
                if len(new_cn) >  max_name_length:
                    new_cn = new_cn[:max_name_length]
                cn_query = name_query("You might have forgotten the date code.", computer_name, new_cn)
                if cn_query == computer_name:
                    return False
                else:
                    return cn_query

            elif no_year_dash_match:
                print("Missing a year")
                year_code = str(date.today().year)[-2:]
                new_cn = year_code + computer_name
                if len(new_cn) >  max_name_length:
                    new_cn = new_cn[:max_name_length]
                new_cn = new_cn.replace("-", "L")
                cn_query = name_query("You might have forgotten the date code, and dashes should be replaced with an L or C.", computer_name, new_cn)
                if cn_query == computer_name:
                    return False
                else:
                    return cn_query
            elif dash_match:
                new_cn = computer_name.replace("-", "L")
                cn_query = name_query("It looks like you used a dash instead of an L or C.", computer_name, new_cn)
                if cn_query == computer_name:
                    return False
                else:
                    return cn_query
            else:
                new_cn = name_error(computer_name)
                if new_cn == computer_name:
                    return False
                else:
                    return new_cn

    elif computer_use_type == "Use 6":
        return False


# Returns True if verified, False if not verified
def verify_config(config, computer_name, asset_tag, computer_use_type, username=None):
    sg.theme('LightGrey1')
    title_font = ("Helvetica", 16, "bold")
    font = ("Helvetica", 16)
    buttons = [[sg.Button("Start!", key="OK", size=(15,1)), sg.Button("Wait, go back!", key="CANCEL", size=(15,1))]]
    if username != None and username != "":
        layout = [  [sg.Text("Please verify that these are all correct before starting the configuration", font=title_font)],
                    [sg.Text("Configuration: ", font=title_font), sg.Text(config, font=font)],
                    [sg.Text("Computer Name: ", font=title_font), sg.Text(computer_name, font=font)],
                    [sg.Text("Asset Tag: ", font=title_font), sg.Text(asset_tag, font=font)],
                    [sg.Text("Use Type: ", font=title_font), sg.Text(computer_use_type, font=font)],
                    [sg.Text("Username: ", font=title_font), sg.Text(username, font=font)],
                    [sg.Col(buttons, justification='center', vertical_alignment='center')]]
    else:
        layout = [  [sg.Text("Please verify that these are all correct before starting the configuration", font=title_font)],
                    [sg.Text("Configuration: ", font=title_font), sg.Text(config, font=font)],
                    [sg.Text("Computer Name: ", font=title_font), sg.Text(computer_name, font=font)],
                    [sg.Text("Asset Tag: ", font=title_font), sg.Text(asset_tag, font=font)],
                    [sg.Text("Use Type: ", font=title_font), sg.Text(computer_use_type, font=font)],
                    [sg.Col(buttons, justification='center', vertical_alignment='center')]]
    
    window = sg.Window("Handy Dandy Configuration Information Verification Assistant", layout, finalize=True)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "CANCEL": # if user closes window or clicks cancel
            window.close()
            return False
        elif event == "OK":
            window.close()
            return True
    

main()