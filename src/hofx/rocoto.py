from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RocotoConfigError(Exception):
    pass


class Rocoto:

    def __init__(self, suite_config, xml='workflow.xml'):
        '''
        Initialize a Rocoto object given a configuration dictionary
        :param suite_config: Rocoto suite generation configuration
        :type suite_config: dict

        '''
        self.suite_config = suite_config
        self.workflow_xml = xml

    def __call__(self):
        pass

    def suite_definition_path(self):
        '''
        Return the path to the input suite configuration
        '''
        return self.suite_config


    def write_xml(self):

        xml = []

        xml.append('<?xml version="1.0"?>\n')
        xml.append('<!DOCTYPE workflow\n')
        xml.append('[\n')

        # preamble
        xml.append(self.doc_opening)

        # entities
        xml.append(self.entities)

        strings.append('\n')
        strings.append(']>\n')
        strings.append('\n')

        xml.append(self.workflow_tag_begin)

        xml.append(self.cycle_logs)
        xml.append(self.cycle_definitions)
        xml.append(self.workflow_tasks)

        xml.append('\n</workflow>\n')  # workflow tag end

        with open(self.xmlfile, 'w') as fh:
            fh.write(''.join(xml))

        return


    def add_comment(comment):
        strings = []
        strings.append(f'<!-- {comment} -->')
        return ''.join(strings)


    @staticproperty
    def add_line(line):
        return f'{line}'

    @property
    def add_new_line:
        return '\n'

    @property
    def _opening:
        '''
        create the xml opening doc block
        '''

        strings = []

        strings.append('\t<!--\n')
        strings.append('\tPROGRAM\n')
        strings.append('\t\tMain workflow manager\n')
        strings.append('\n')
        strings.append('\tNOTES:\n')
        strings.append(f'\t\tThis workflow was automatically generated at {datetime.now()}\n')
        strings.append('\t-->\n')

        return ''.join(strings)


    def create_workflow_tags(cfg):

        realtime = cfg.get('realtime', 'F')
        scheduler = cfg.get('scheduler')
        cycle_throttle = cfg.get('cycle_throttle', 3)
        task_throttle = cfg.get('task_throttle', 10)

        strings = []
        strings.append(f'<workflow realtime="{realtime}" scheduler="{scheduler}" cyclethrottle="{cycle_throttle}" taskthrottle="{task_throttle}">\n')
        strings.append('</workflow>')

        return strings


    def create_log(cfg):

        verbosity = cfg.get('verbosity', 10)
        logfile = cfg.get('logfile', 'logs/@Y@m@d@H.log')

        return f'<log verbosity="{verbosity}"><cyclestr>{logfile}</cyclestr></log>\n'


    def create_cycledef(cfg):

        cycle_group = cfg.get('cycle_group')
        cycle_start = cfg.get('cycle_start')
        cycle_stop = cfg.get('cycle_stop')
        cycle_step = cfg.get('cycle_step')

        return f'<cycledef group="{cycle_group}">{cycle_start} {cycle_stop} {cycle_step}</cycledef>\n'


    def create_metatask(task_dict, metatask_dict):
        '''
        create a Rocoto metatask given a dictionary containing task and metatask information
        :param metatask_dict: metatask key-value parameters
        :type metatask_dict: dict
        :param task_dict: task key-value parameters
        :type task_dict: dict
        :return: Rocoto metatask
        :rtype: list
        '''

        # Grab metatask info from the metatask_dict
        metataskname = metatask_dict.get('metataskname', 'demometatask')
        varname = metatask_dict.get('varname', 'demovar')
        varval = metatask_dict.get('varval', 1)
        vardict = metatask_dict.get('vardict', None)

        strings = []

        strings.append(f'<metatask name="{metataskname}">\n')
        strings.append('\n')
        strings.append(f'\t<var name="{varname}">{str(varval)}</var>\n')
        if vardict is not None:
            for key in list(vardict.keys()):
                value = str(vardict[key])
                strings.append(f'\t<var name="{key}">{value}</var>\n')
        strings.append('\n')
        tasklines = create_task(task_dict)
        for tl in tasklines:
            strings.append(f'{tl}') if tl == '\n' else strings.append(f'\t{tl}')
        strings.append('\n')
        strings.append('</metatask>\n')

        return strings


    def create_task(task_dict):
        '''
        create a Rocoto task given a dictionary containing task information
        :param task_dict: task key-value parameters
        :type task_dict: dict
        :return: Rocoto task
        :rtype: list
        '''

        # Grab task info from the task_dict
        taskname = task_dict.get('taskname', 'demotask')
        cycledef = task_dict.get('cycledef', 'democycle')
        maxtries = str(task_dict.get('maxtries', 3))
        final = task_dict.get('final', False)
        command = task_dict.get('command', 'sleep 10')
        jobname = task_dict.get('jobname', 'demojob')
        account = task_dict.get('account', 'batch')
        queue = task_dict.get('queue', 'debug')
        partition = task_dict.get('partition', None)
        walltime = task_dict.get('walltime', '00:01:00')
        log = task_dict.get('log', 'demo.log')
        native = task_dict.get('native', None)
        memory = task_dict.get('memory', None)
        resources = task_dict.get('resources', None)
        envar = task_dict.get('envar', None)
        dependency = task_dict.get('dependency', None)

        str_final = ' final="true"' if final else ''
        envar = envar if isinstance(envar, list) else [envar]

        strings = []

        strings.append(f'<task name="{taskname}" cycledefs="{cycledef}" maxtries="{maxtries}"{str_final}>\n')
        strings.append('\n')
        strings.append(f'\t<command>{command}</command>\n')
        strings.append('\n')
        strings.append(f'\t<jobname><cyclestr>{jobname}</cyclestr></jobname>\n')
        strings.append(f'\t<account>{account}</account>\n')
        strings.append(f'\t<queue>{queue}</queue>\n')
        if partition is not None:
            strings.append(f'\t<partition>{partition}</partition>\n')
        if resources is not None:
            strings.append('\t{resources}\n')
        strings.append(f'\t<walltime>{walltime}</walltime>\n')
        if memory is not None:
            strings.append(f'\t<memory>{memory}</memory>\n')
        if native is not None:
            strings.append(f'\t<native>{native}</native>\n')
        strings.append('\n')
        strings.append(f'\t<join><cyclestr>{log}</cyclestr></join>\n')
        strings.append('\n')

        if envar[0] is not None:
            for e in envar:
                strings.append(f'\t{e}\n')
            strings.append('\n')

        if dependency is not None:
            strings.append('\t<dependency>\n')
            for d in dependency:
                strings.append(f'\t\t{d}\n')
            strings.append('\t</dependency>\n')
            strings.append('\n')

        strings.append('</task>\n')

        return strings


    def add_dependency(dep_dict):
        '''
        create a simple Rocoto dependency given a dictionary with dependency information
        :param dep_dict: dependency key-value parameters
        :type dep_dict: dict
        :return: Rocoto simple dependency
        :rtype: str
        '''

        dep_condition = dep_dict.get('condition', None)
        dep_type = dep_dict.get('type', None)

        if dep_type in ['task', 'metatask']:
            string = self._add_task_tag(dep_dict)
        elif dep_type in ['data']:
            string = self._add_data_tag(dep_dict)
        elif dep_type in ['cycleexist']:
            string = self._add_cycle_tag(dep_dict)
        elif dep_type in ['streq', 'strneq']:
            string = self._add_streq_tag(dep_dict)
        else:
            raise KeyError(f'Unknown dependency type {dep_type}')

        if dep_condition is not None:
            string = f'<{dep_condition}>{string}</{dep_condition}>'

        return string


    def _add_task_tag(dep_dict):
        '''
        create a simple task or metatask tag
        :param dep_dict: dependency key-value parameters
        :type dep_dict: dict
        :return: Rocoto simple task or metatask dependency
        :rtype: str
        '''

        dep_type = dep_dict.get('type', None)
        dep_name = dep_dict.get('name', None)
        dep_offset = dep_dict.get('offset', None)

        if dep_name is None:
            raise KeyError(f'a {dep_type} name is necessary for {dep_type} dependency')

        string = '<'
        string += f'{dep_type}dep {dep_type}="{dep_name}"'
        if dep_offset is not None:
            string += f' cycle_offset="{dep_offset}"'
        string += '/>'

        return string


    def _add_data_tag(dep_dict):
        '''
        create a simple data tag
        :param dep_dict: dependency key-value parameters
        :type dep_dict: dict
        :return: Rocoto simple task or metatask dependency
        :rtype: str
        '''

        dep_type = dep_dict.get('type', None)
        dep_data = dep_dict.get('data', None)
        dep_offset = dep_dict.get('offset', None)

        if dep_data is None:
            raise KeyError(f'a data value is necessary for {dep_type} dependency')

        if dep_offset is None:
            if '@' in dep_data:
                offset_string_b = '<cyclestr>'
                offset_string_e = '</cyclestr>'
            else:
                offset_string_b = ''
                offset_string_e = ''
        else:
            offset_string_b = f'<cyclestr offset="{dep_offset}">'
            offset_string_e = '</cyclestr>'

        string = f'<datadep>{offset_string_b}{dep_data}{offset_string_e}</datadep>'

        return string


    def _add_cycle_tag(dep_dict):
        '''
        create a simple cycle exist tag
        :param dep_dict: dependency key-value parameters
        :type dep_dict: dict
        :return: Rocoto simple task or metatask dependency
        :rtype: str
        '''

        dep_type = dep_dict.get('type', None)
        dep_offset = dep_dict.get('offset', None)

        if dep_offset is None:
            raise KeyError(f'an offset value is necessary for {dep_type} dependency')

        string = f'<cycleexistdep cycle_offset="{dep_offset}"/>'

        return string


    def _add_streq_tag(dep_dict):
        '''
        create a simple string comparison tag
        :param dep_dict: dependency key-value parameters
        :type dep_dict: dict
        :return: Rocoto simple task or metatask dependency
        :rtype: str
        '''

        dep_type = dep_dict.get('type', None)
        dep_left = dep_dict.get('left', None)
        dep_right = dep_dict.get('right', None)

        fail = False
        msg = ''
        if dep_left is None:
            msg += f'a left value is necessary for {dep_type} dependency'
            fail = True
        if dep_right is None:
            if fail:
                msg += '\n'
            msg += f'a right value is necessary for {dep_type} dependency'
            fail = True
        if fail:
            raise KeyError(msg)

        string = f'<{dep_type}><left>{dep_left}</left><right>{dep_right}</right></{dep_type}>'

        return string


    def _traverse(o, tree_types=(list, tuple)):
        '''
        Traverse through a list of lists or tuples and yeild the value
        Objective is to flatten a list of lists or tuples
        :param o: list of lists or not
        :type o: list, tuple, scalar
        :param tree_types: trees to travers
        :type tree_types: tuple
        :return: value in the list or tuple
        :rtype: scalar
        '''

        if isinstance(o, tree_types):
            for value in o:
                for subvalue in self._traverse(value, tree_types):
                    yield subvalue
        else:
            yield o


    def create_dependency(dep_condition=None, dep=None):
        '''
        create a compound dependency given a list of dependendies, and compounding condition
        the list of dependencies are created using add_dependency
        :param dep_condition: dependency condition
        :type dep_condition: boolean e.g. and, or, true, false
        :param dep: dependency
        :type dep: str or list
        :return: Rocoto compound dependency
        :rtype: list
        '''

        dep = dep if isinstance(dep, list) else [dep]

        strings = []

        if dep_condition is not None:
            strings.append(f'<{dep_condition}>')

        if dep[0] is not None:
            for d in dep:
                if dep_condition is None:
                    strings.append(f'{d}')
                else:
                    for e in self._traverse(d):
                        strings.append(f'\t{e}')

        if dep_condition is not None:
            strings.append(f'</{dep_condition}>')

        return strings


    def create_envar(name=None, value=None):
        '''
        create an Rocoto environment variable given name and value
        returns the environment variable as a string
        :param name: name of the environment variable
        :type name: str
        :param value: value of the environment variable
        :type value: str or float or int or unicode
        :return: Rocoto environment variable key-value pair
        :rtype: str
        '''

        return f'<envar><name>{name}</name><value>{value}</value></envar>\n'


    def create_envar_from_dict(config):
        envars = []
        for k in config.keys():
            envars.append(self.create_envar(name=k, value=k[v]))
        return envars


    def create_entity(name=None, value=None):
        '''
        create an Rocoto entity variable given name and value
        returns the entity variable as a string
        :param name: name of the entity variable
        :type name: str
        :param value: value of the entity variable
        :type value: str or float or int or unicode
        :return: Rocoto entity variable key-value pair
        :rtype: str
        '''

        return f'<!ENTITY {name} "{value}">\n'

    def create_entity_from_dict(config):
        entities = []
        for k in config.keys():
            entities.append(self.create_entity(name=k, value=k[v]))
