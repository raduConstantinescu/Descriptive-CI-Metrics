"""Module for mining file information"""
from enum import Enum

from modules.exception import ModuleParamException
from modules.mining_module import MiningModule


class FileModule(MiningModule):
    """
    This class mines file information

    Attributes
    ----------
    files : PaginatedList[ContentFile]
        An object where you can extract all kinds of file information from
    json : dict
        Dictionary containing information about the files
    params: list
        A list that contains what information you want from the repository in this module

    Methods
    -------
    mine()
        The main entry point to this class. Calling this function will mine all the data in the body
    _extract_param_info(param)
        Calls the right function given a parameter from self.params
    _extract_creation_date()
        Extracts the creation date of the issues
    _extract_close_date()
        Extracts the close date of the issues
    """

    def __init__(self, params=None):
        self.files = super().repo.get_contents('')
        self.json = {'files': {}}
        self.params = [f.value for f in FileParams] if params is None else params

    def mine(self):
        for param in self.params:
            if param in (FileParams.FILE_CHANGE_COUNT, FileParams.FILE_CHANGE_COUNT.value):
                self._extract_file_change_count()
            else:
                raise ModuleParamException("Module does not have param: " + str(param))
        return self.json

    def _extract_file_change_count(self):
        self.json['files']['file_change_count'] = []

        contents = self.repo.get_contents(path='')
        while contents:
            file_content = contents.pop(0)
            if file_content.type == 'dir':
                contents.extend(self.repo.get_contents(path=file_content.path))
            else:
                if file_content.path.endswith('.py'):
                    commits = self.repo.get_commits(path=file_content.path)
                    num_changes = commits.totalCount
                    commit_dates = [commit.commit.author.date for commit in commits]

                    file_info = {
                        'total_times_changed': num_changes,
                        'when_changed': commit_dates
                    }

                    self.json['files']['file_change_count'].append({file_content.name: file_info})


class FileParams(Enum):
    """
    A class that holds enum values for the functions in the file_module class
    """
    FILE_CHANGE_COUNT = 'file_change_count'
