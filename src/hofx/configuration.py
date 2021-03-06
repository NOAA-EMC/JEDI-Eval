from solo.yaml_file import YAMLFile
from solo.template import TemplateConstants, Template
from hofx.tools import replace_vars

__all__ = ['read_yaml', 'clean_yaml', 'clean_obs_yaml']

def read_yaml(yamls, template=None, config_in=None):
    """
    read_yaml(yamls, template=None)
    read in configuration from one or more YAML files
     - yamls is either a path to one YAML file
       or a list of paths of files to combine together
     - template=None by default, is a path to a YAML
       file to use as a template for final output
     - config_in=None by default, is a dictionary containing
       keys,values that are dynamically generated/in memory
    """
    if isinstance(yamls, list):
        # read multiple YAML files
        config = YAMLFile(yamls[0])
        for yf in yamls[1:]:
            tmp_config = YAMLFile(yf)
            config.update(tmp_config)
    else:
        # read a single file
        config = YAMLFile(yamls)
    if config_in is not None:
        config.update(config_in)
    if template is not None:
        # read in a template YAML file for final config contents
        config_temp = YAMLFile(template)
        config_out = YAMLFile(template)
        # combine template with previous config
        config_out.update(config)
    else:
        config_out = config
    # replace variables in config
    config_out = replace_vars(config_out)
    # check for includes and add them
    config_out = _include_yaml(config_out)
    # do another find/replace now that there are includes
    config_out = replace_vars(config_out)
    # do a couple of recursive updates for good measure
    config_out = update_config(config_out)
    config_out = update_config(config_out)
    if template is not None:
        # remove things not in the template for final output
        config_out = clean_yaml(config_out, config_temp)
    return config_out

def _include_yaml(config):
    # look for the include yaml string and if it exists
    # 'include' that YAML in the config dictionary
    incstr = '$<<'
    for rootkey, rootval in config.items():
        if type(rootval) is list:
            # handle lists in the dictionary
            newlist = []
            for item in rootval:
                if incstr in item:
                    incpath = item.replace(incstr, '').strip()
                    newconfig = YAMLFile(incpath)
                    newlist.append(newconfig)
                else:
                    newlist.append(item) # keeps something in the list if it is not an include
            config[rootkey] = newlist
        else:
            # handle single includes
            if incstr in rootval:
                incpath = rootval.replace(incstr, '').strip()
                newconfig = YAMLFile(incpath)
                config[rootkey] = newconfig
    return config

def _iter_config(config, subconfig):
    subconfig = Template.substitute_structure(subconfig, TemplateConstants.DOLLAR_PARENTHESES, config.get)
    subconfig = _include_yaml(subconfig)
    subconfig = replace_vars(subconfig)
    for key, value in subconfig.items():
        if isinstance(value, dict):
            value = _iter_config(config, value)
    return subconfig

def update_config(config):
    # drill through configuration and add includes and replace vars
    config = replace_vars(config)
    config = _include_yaml(config)
    config = replace_vars(config)
    for key, value in config.items():
        if isinstance(value, dict):
            value = _iter_config(config, value)
    return config


def clean_yaml(config_out, config_template):
    # remove top level keys in config_out if they do not appear in config_template
    keys_to_del = []
    for key, value in config_out.items():
        if key not in config_template:
            keys_to_del.append(key)
    for key in keys_to_del:
        del config_out[key]
    return config_out

def clean_obs_yaml(config):
    """
    clean_obs_yaml(config)
      for an input configuration dictionary, config, remove extra things like
      obs filters, etc. that make the YAML long that are not needed for
      diag plotting, analysis, etc.
    """
    for key, value in config.items():
        if isinstance(value, dict):
            for key2, value2 in value.items():
                if isinstance(value2, dict):
                    for key3, value3 in value2.items():
                        if key3 == 'observations':
                            for ob in value3:
                                delkeys = []
                                for key4, value4 in ob.items():
                                    if key4 in ['obs bias', 'obs filters']:
                                       delkeys.append(key4)
                                for k in delkeys:
                                    del ob[k]
    return config
