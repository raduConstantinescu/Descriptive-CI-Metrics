"""This module contains the YmlAnalyzer class for loading and analyzing YAML files"""

import ruamel.yaml as yaml
import numpy as np
import itertools

class YmlAnalyzer:
    """Class for loading and analyzing YAML files"""

    def __init__(self, repos):
        """Initializes the YmlAnalyzer class by loading the YAML files as objects into the repos dictionary"""
        self.repos = repos

        for repo_name, repo in self.repos.items():
            for _, workflow_file in enumerate(repo['workflow_files']):
                file_path = "out/" + repo_name + "/" + workflow_file['platform'].replace("_","-") + "/" + workflow_file['name']
                with open(file_path, 'r') as f:
                    workflow_file['config_content'] = yaml.round_trip_load(f)

    def aggregate_triggers(self, include_workflows=False):
        """Aggregates the triggers and modifiers used in the YAML files"""
        used_triggers = {}
        trigger_used = { "yes": 0, "no": 0 }

        for repo_name, repo in self.repos.items():
            for _, workflow_file in enumerate(repo['workflow_files']):
                if workflow_file['platform'] == 'github_actions':

                    workflow_meta = {
                        'repo': repo_name,
                        'name': workflow_file['name'],
                    } if include_workflows else None

                    config = workflow_file['config_content']

                    if 'on' in config:
                        triggers = config['on']
                        
                        self.__add_triggers_to_array(used_triggers, triggers, workflow_meta)

                        trigger_used['yes'] = trigger_used['yes'] + 1
                    else:
                        trigger_used['no'] = trigger_used['no'] + 1

        return used_triggers

    def aggregate_triggers_coocurrance(self, trigger_types):
        coorcurance = np.zeros((len(trigger_types), len(trigger_types)))

        for _, repo in self.repos.items():
            for _, workflow_file in enumerate(repo['workflow_files']):
                if workflow_file['platform'] == 'github_actions':

                    config = workflow_file['config_content']
                    if 'on' in config:
                        triggers = config['on']

                        trigger_names = []

                        if isinstance(triggers, list) and len(triggers) > 1:
                            trigger_names = sorted(triggers)
                        elif isinstance(triggers, dict) and len(triggers) > 1:
                            trigger_names = sorted(list(triggers.keys()))

                        combinations = itertools.combinations(trigger_names, 2)

                        for a, b in combinations:
                            x = trigger_types.index(a)
                            y = trigger_types.index(b)
                            coorcurance[x][y] = coorcurance[x][y] + 1

        return sorted(trigger_types), coorcurance


    def __add_triggers_to_array(self, array, triggers, workflow_meta):
        """Unpacks and adds the triggers to the array dependent on the type of the triggers"""
        if isinstance(triggers, str):
            self.__add_trigger_to_array(array, triggers, workflow_meta)
            self.__add_modifier_to_dict(array[triggers]['modifiers'], 'none')

        elif isinstance(triggers, list):
            for trigger in triggers:
                self.__add_trigger_to_array(array, trigger, workflow_meta)
                self.__add_modifier_to_dict(array[trigger]['modifiers'], 'none')

        elif isinstance(triggers, dict):
            for trigger, modifiers in triggers.items():
                self.__add_trigger_to_array(array, trigger, workflow_meta)
                self.__add_modifiers_to_dict(array[trigger]['modifiers'], modifiers)

    def __add_trigger_to_array(self, array, trigger, workflow_meta: None):
        """Adds the trigger to the array if it does not exist yet, otherwise it increments the count"""
        if trigger not in array:
            array[trigger] = {
                "count": 0,
                "workflows": [],
                "modifiers": {}
            }

        array[trigger]["count"] = array[trigger]["count"] + 1

        if workflow_meta:
            array[trigger]["workflows"].append(workflow_meta)


    def __add_modifiers_to_dict(self, dictionary, modifiers):
        if modifiers is None:
            self.__add_modifier_to_dict(dictionary, 'none')

        elif isinstance(modifiers, list):
            for modifier in modifiers:
                self.__add_modifier_to_dict(dictionary, str(modifier))

        elif isinstance(modifiers, dict):
            for modifier, _ in modifiers.items():
                self.__add_modifier_to_dict(dictionary, modifier)


    def __add_modifier_to_dict(self, dictionary, modifier):
        if modifier not in dictionary:
            dictionary[modifier] = 0

        dictionary[modifier] = dictionary[modifier] + 1
