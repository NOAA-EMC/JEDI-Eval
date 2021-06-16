import platform
from solo.template import Template

__all__ = ['detect_host', 'process_environment_variables', 'replace_vars']


##### REMOVE BELOW function??? #####
def process_environment_variables(request):
    """
        Traverse the dictionary in depth to find and replace all
        occurrences of ${var_name}, var_name being an environment variable
    """
    return Template.substitute_structure_from_environment(request)

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

def replace_vars(config):
    # use SOLO to replace variables in the configuration dictionary
    # as appropriate with either other dictionary key/value pairs
    # or environment variables
    config = Template.substitute_structure_from_environment(config)
    config = Template.substitute_with_dependencies(config, TemplateConstants.DOLLAR_PARENTHESES)
    config = Template.substitute_structure(config, TemplateConstants.DOUBLE_CURLY_BRACES, config.get)
    return config
