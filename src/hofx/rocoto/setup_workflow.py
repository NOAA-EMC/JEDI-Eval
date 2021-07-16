#!/usr/bin/env python
import os
import sys
import yaml
import platform

# local function to identify machine
def detect_host():
    system = platform.system().lower()
    node = platform.node().lower()
    if system == 'linux':
        if node.find('orion') != -1:
            return 'orion'
        elif node.find('hfe') != -1:
            return 'hera'
    elif system == 'darwin':
        return 'mac'
    else:
        return None

# local function to return search_key value from a search_list
def set_key(search_key,search_list):
    res = [val for key, val in search_list.items() if search_key in key]
    key_value=" "
    str1 = " "
    key_value=str1.join(res)
    return key_value



# Main body of script
#
# Open and read user configured experiment.yaml file
with open("../cfg/expdir/experiment.yaml") as expyml:
   parsed_expyml=yaml.safe_load(expyml)


# Detect machine
machine=detect_host()


# Extract values from user configure yaml
#   note:  add '00' for seconds to begin and end dates
search_key='expname'
expname=set_key(search_key,parsed_expyml)

search_key='begdate'
begdate=set_key(search_key,parsed_expyml) + '00'

search_key='enddate'
enddate=set_key(search_key,parsed_expyml) + '00'

search_key='hofx_homedir'
hofx_homedir=set_key(search_key,parsed_expyml)

search_key='wrkdir'
wrkdir=set_key(search_key,parsed_expyml)


# Load extracte values into list.  Echo values to stdout
replacements = {
    'expname': expname,
    'begdate': begdate,
    'enddate': enddate,
    'hofx_homedir': hofx_homedir,
    'wrkdir': wrkdir,
    'platform': machine,
}

print(' ')
print("Extract following settings")
for src, target in replacements.items():
   print(src, target)


# Create filename for workflow xml
expxml=expname + '.xml'
print(' ')
print('Create xml: {}'.format(expxml))


# Write workflow xml
with open("hofx.xml", 'r') as xmlin:
  with open(expxml, 'w') as xmlout:
    for line in xmlin:
      for src, target in replacements.items():
        line = line.replace(src, target)
      xmlout.write(line)

