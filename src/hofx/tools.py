import platform
from solo.template import Template

__all__ = ['detect_host', 'process_environment_variables']


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
        elif n.find('hfe') != -1:
            return 'hera'
    elif system == 'darwin':
        return 'mac'
    else:
        return None
