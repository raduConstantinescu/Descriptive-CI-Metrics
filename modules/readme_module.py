"""Module for mining readme information"""
import dataclasses
from enum import Enum
import re
from modules.exception import ModuleParamException
from modules.mining_module import MiningModule

@dataclasses.dataclass
class ReadMeModule(MiningModule):
    """
    This class mines readme information

    Parameters
    ----------
    params : list
        List of parameters to mine.
        Possible values are: 'content', 'length'
    verbose : bool
        Whether or not to print out information about the mining process

    Attributes
    ----------
    readme : str
        The readme of the repository
    json : dict
        Dictionary containing information about the readme
    params : list
        List of parameters to mine

    Methods
    -------
    mine()
        The main entry point to this class. Calling this function will mine all the data in the body
    _extract_param_info(param)
        Calls the right function given a parameter from self.params
    _extract_readme()
        Extracts the readme from a repository
    _extract_readme_length()
        Extracts the length of the readme from a repository
    _preprocess_readme()
        Preprocesses the readme
    """
    def __init__(self, params=None, verbose=False):
        if verbose:
            print(f"Extracting textual data for repo {super().repo.full_name}")

        try:
            self.readme = super().repo.get_readme().decoded_content.decode("utf-8")
            self._preprocess_readme()
        # pylint: disable=broad-except
        except Exception as exception:
            if verbose:
                print(f"Failed to extract readme for repo {super().repo.full_name}. Error: {exception}")
            self.readme = ""

        self.params = [c.value for c in ReadMeParams] if params is None else params
        self.json = {'readme': {}}

    def mine(self):
        """Mines all the data in self.params and returns a dictionary with all the mined data"""
        for param in self.params:
            self._extract_param_info(param)

        return self.json

    def _extract_param_info(self, param):
        if param in (ReadMeParams.CONTENT, ReadMeParams.CONTENT.value):
            self._extract_readme()
        elif param in (ReadMeParams.LENGTH, ReadMeParams.LENGTH.value):
            self._extract_readme_length()
        else:
            raise ModuleParamException("Module does not have param: " + str(param))

    def _extract_readme(self):
        self.json['readme']['content'] = self.readme

    def _extract_readme_length(self):
        self.json['readme']['length'] = len(self.readme)

    def _preprocess_readme(self):
        # Remove newlines
        self.readme = self.readme.replace("\n", " ")
        # Remove urls
        self.readme = self._remove_urls(self.readme)
        # Remove unicode characters
        self.readme = self.readme.encode('ascii', 'ignore').decode('ascii')
        # Replace every special character with a space
        self.readme = re.sub(r'[^a-zA-Z0-9]', ' ', self.readme)
        # Remove multiple spaces
        self.readme = re.sub(r'\s+', ' ', self.readme).strip()

    def _remove_urls(self, text):
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        cleaned_text = re.sub(url_pattern, '', text)

        return cleaned_text

class ReadMeParams(Enum):
    """
    A class that holds enum values for the functions in the readme_module class
    """
    CONTENT = "content"
    LENGTH = "length"
