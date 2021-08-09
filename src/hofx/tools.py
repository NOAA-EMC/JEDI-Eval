import os
import platform
from solo.template import Template, TemplateConstants
from solo.date import JediDate, DateIncrement, Minute
from solo.ioda import Ioda

__all__ = ['detect_host', 'process_environment_variables', 'replace_vars', 'Window']


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
    config = Template.substitute_with_dependencies(config, config, TemplateConstants.DOLLAR_PARENTHESES)
    config = Template.substitute_structure(config, TemplateConstants.DOUBLE_CURLY_BRACES, config.get)
    return config

def merge_diags(files, outfile):
    """
    merge_diags(files, outfile)
      for a list of files `files`, concatenate them into one `outfile`
    """
    if (len(files)) > 0:
        ioda = Ioda('diags')
        ioda.concat_files(files, outfile)
    else:
        print('No files to concatenate!')

class Window:

    def __init__(self, config):
        self._config = config
        self.window_length = DateIncrement(config.get('window_length', 'PT6H')) # length of the assimilation window (beginning to end)
        self.window_offset = DateIncrement(config.get('window_offset', 'PT3H')) # offset from end of the window to "analysis time"
        self.step_cycle = DateIncrement(config.get('step_cycle', 'PT6H')) # Cadence
        self.window_type = config.get('window_type', '3d') # 3D or 4D windows
        self.bg_frequency = DateIncrement(config.get('bg_frequency', self.step_cycle)) # Frequency of backgrounds
        self.bg_step = DateIncrement(config.get('bg_step', self.step_cycle)) # Cadence
        self.info

    @property
    def info(self):
        print('Information about the Window object:')
        print(f'\twindow_length = {self.window_length}')
        print(f'\twindow_offset = {self.window_offset}')
        print(f'\twindow_type   = {self.window_type}')
        print(f'\tstep_cycle    = {self.step_cycle}')
        print(f'\tbg_frequency  = {self.bg_frequency}')
        print(f'\tbg_step       = {self.bg_step}')
        return

    @staticmethod
    def analysis_time(current_date):
        return str(JediDate(current_date))

    def window_end(self, current_date):
        return str(JediDate(current_date) + self.window_offset)

    def window_begin(self, current_date):
        return str(JediDate(current_date) + self.window_offset - self.window_length)

    # JEDI calls previous_cycle as background_time
    def background_time(self, current_date):
        return str(JediDate(current_date) - self.bg_step)

    def background_steps(self, current_date):
        if self.window_type.lower() == '3d':
            return [str(self.step_cycle)]

        window_begin = Minute(self.window_begin(current_date))
        background_time = Minute(self.background_time(current_date))
        # calculate the initial step in hours
        initial_step = DateIncrement(seconds=(window_begin - background_time) * 60)
        steps = [str(initial_step)]
        frequency = DateIncrement(self.bg_frequency)
        date = window_begin + frequency
        end = window_begin + DateIncrement(self.window_length)
        if end - date >= frequency.total_seconds() / 60:
            while date <= end:
                steps.append(str(DateIncrement(seconds=(date - background_time) * 60)))
                date += frequency
        return steps

    def details(self, current_date):
        config = dict(
                window_begin = self.window_begin(current_date),
                window_end = self.window_end(current_date),
                background_steps = self.background_steps(current_date)
                )
        return config
