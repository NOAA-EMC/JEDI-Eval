#!/usr/bin/env python
import os
import sys
import yaml
import hofx
import click

@click.command()
@click.option('--expxmldir', default='.', help='directory to which xml file is written (default ./)')
@click.argument('expxmldir', default='.', type=click.Path(exists=True))
def setup_workflow(expxmldir):
    """
    read in YAML file containing user experiment settings and
    create a rocoto xml file to cycle through specified dates.
    """

#   local function to return search_key value from a search_list
    def set_key(search_key,search_list):
        res = [val for key, val in search_list.items() if search_key in key]
        key_value=" "
        str1 = " "
        key_value=str1.join(res)
        return key_value

    # Open and read user configured experiment.yaml file
    with open("../cfg/expdir/experiment.yaml") as expyml:
       parsed_expyml=yaml.safe_load(expyml)

    # Detect machine
    machine = hofx.tools.detect_host()

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

#   Create filename for workflow xml
    expxml=expxmldir + '/' + expname + '.xml'
    print(' ')
    print('Create xml: {}'.format(expxml))

#   Write workflow xml
    with open("../cfg/templates/hofx.xml", 'r') as xmlin:
      with open(expxml, 'w') as xmlout:
        for line in xmlin:
          for src, target in replacements.items():
            line = line.replace(src, target)
          xmlout.write(line)

if __name__ == '__main__':
    setup_workflow()


