#!/usr/bin/env python
import os
import sys
import yaml
import platform

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

with open("../cfg/expdir/experiment.yaml") as expyml:
   parsed_expyml=yaml.safe_load(expyml)

machine=detect_host()

search_key='expname'
res = [val for key, val in parsed_expyml.items() if search_key in key]
expname=" "
str1 = " "
expname=str1.join(res)

search_key='begdate'
res = [val for key, val in parsed_expyml.items() if search_key in key]
begdate=" "
str1 = " "
begdate=str1.join(res) + '00'

search_key='enddate'
res = [val for key, val in parsed_expyml.items() if search_key in key]
enddate=" "
str1 = " "
enddate=str1.join(res) + '00'

search_key='hofx_homedir'
res = [val for key, val in parsed_expyml.items() if search_key in key]
hofx_homedir=" "
str1 = " "
hofx_homedir=str1.join(res)

search_key='wrkdir'
res = [val for key, val in parsed_expyml.items() if search_key in key]
wrkdir=" "
str1 = " "
wrkdir=str1.join(res)

##search_key='platform'
##res = [val for key, val in parsed_expyml.items() if search_key in key]
##platform=" "
##str1 = " "
##platform=str1.join(res)


replacements = {
    'expname': expname,
    'begdate': begdate,
    'enddate': enddate,
    'hofx_homedir': hofx_homedir,
    'wrkdir': wrkdir,
    'platform': machine,
}


for src, target in replacements.items():
   print(src, target)

expxml=expname + '.xml'
print(expxml)

with open("hofx.xml", 'r') as xmlin:
  with open(expxml, 'w') as xmlout:
    for line in xmlin:
      for src, target in replacements.items():
        line = line.replace(src, target)
      xmlout.write(line)

