"""Module for mining workflow config files"""
import dataclasses
import os
from enum import Enum

from github import GithubException

from modules.commits_module import CommitParams, CommitsModule
from modules.exception import ModuleParamException
from modules.mining_module import MiningModule


@dataclasses.dataclass
class WorkflowConfigModule(MiningModule):
    """
    This class mines workflow config .yml files

    Attributes
    ----------
    json : dict
        Dictionary containing information about the workflow files
    params: list
        A list that contains what information you want from the repository in this module.

    Methods
    -------
    mine()
        The main entry point to this class. Calling this function will mine all the data in
        self.params.
    _extract_github_actions_config()
        Extracts the GitHub actions workflow config files from a repository
    _extract_travis_ci_config()
        Extracts the TravisCI workflow config files from a repository
    _is_yml_file()
        Checks whether a filename ends with ".yml" or ".yaml"
    _store_config_file()
        Saves a workflow config file to a "out/{repo_name}/{ci_platform}" folder
    """

    # Params, represent the information you want extracted from the Workflow Module.
    # Default behaviour: no params passed: all workflow information extracted.
    def __init__(self, params=None):
        self.json = {
                        'workflow_files': [],
                        'workflow_platforms': {
                            'github_actions': True,
                            'travis_ci': True
                        }
                    }
        self.params = [c.value for c in WorkflowConfigParams] if params is None else params

    def mine(self):
        for param in self.params:
            self._extract_param_info(param=param)
        return self.json

    # Maps Workflow Param Enum to Param Extractor Function
    def _extract_param_info(self, param):
        if param in (WorkflowConfigParams.GITHUB_ACTIONS_CONFIG, WorkflowConfigParams.GITHUB_ACTIONS_CONFIG.value):
            self._extract_github_actions_config()
        elif param in (WorkflowConfigParams.TRAVIS_CI_CONFIG, WorkflowConfigParams.TRAVIS_CI_CONFIG.value):
            self._extract_travis_ci_config()
        elif param in (WorkflowConfigParams.COMMITS, WorkflowConfigParams.COMMITS.value):
            self._extract_commits()
        else:
            raise ModuleParamException("Module does not have param: " + str(param))

    def _extract_github_actions_config(self):
        try:
            contents = super().repo.get_contents(".github/workflows")

            while contents:
                config_file = contents.pop(0)

                if self._is_yml_file(config_file.name):
                    self.json['workflow_files'].append({ 'platform': 'github_actions', 'path': config_file.path})
                    self._store_config_file('github-actions', config_file)
        except GithubException:
            self.json['workflow_platforms']['github_actions'] = False


    def _extract_travis_ci_config(self):
        try:
            contents = super().repo.get_contents("")
            travis_ci_detected = False

            while contents and not travis_ci_detected:
                config_file = contents.pop(0)

                if (self._is_yml_file(config_file.name) and config_file.name.startswith('.travis')):
                    travis_ci_detected = True
                    self.json['workflow_files'].append({ 'platform': 'travis_ci', 'path': config_file.path})
                    self._store_config_file('travis-ci', config_file)

            if not travis_ci_detected:
                self.json['workflow_platforms']['travis_ci'] = False

        except GithubException:
            self.json['workflow_platforms']['travis_ci'] = False

    def _extract_commits(self):
        for file in self.json['workflow_files']:
            print(file)
            commit_module = CommitsModule([CommitParams.COMMIT_META], path=file['path'])
            commits = commit_module.mine()
            file['commits'] = commits['commits']['meta']


    def _is_yml_file(self, filename):
        return filename.endswith('.yml') or filename.endswith('.yaml')

    def _store_config_file(self, platform_name, config_file):
        out_filename = "out/" + super().repo.name + "/" + platform_name + "/" + config_file.name

        os.makedirs(os.path.dirname(out_filename), exist_ok=True)

        with open(out_filename, "w", encoding="utf-8") as out_file:
            out_file.write(config_file.decoded_content.decode("utf-8"))
            out_file.close()


# Parameters of the Workflow Config
class WorkflowConfigParams(Enum):
    """
    A class that holds enum values for the functions in the WorkflowConfigModule class
    """
    GITHUB_ACTIONS_CONFIG = 'github_actions_config'
    TRAVIS_CI_CONFIG = 'travis_ci_config'
    COMMITS = 'commits'
