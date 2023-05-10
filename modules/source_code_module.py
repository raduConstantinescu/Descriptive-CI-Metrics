"""Module for mining source code from a repository"""
import dataclasses
import time
from git import Repo
from modules.mining_module import MiningModule

@dataclasses.dataclass
class SourceCodeModule(MiningModule):
    """
    This class mines source code from a repository

    Parameters
    ----------
    export_dir : str
        The directory where the source code will be exported to
    verbose : bool
        Whether or not to print out information about the mining process

    Attributes
    ----------
    json : dict
        Dictionary containing information about the source code

    Methods
    -------
    mine()
        The main entry point to this class. Calling this function will mine all the data in the body
    """
    def __init__(self, export_dir, verbose=False):
        start_time = time.time()

        if verbose:
            print(f"Cloning repo {super().repo.full_name} to {export_dir}")

        repo_url = f"https://github.com/{super().repo.full_name}.git"
        Repo.clone_from(repo_url, export_dir)
        self.json = {'source_code_dir': export_dir}

        if verbose:
            print(f"Cloning finished in {time.time() - start_time} seconds")

    def mine(self):
        """Returns a dictionary with all the mined data"""
        return self.json
