"""Module for mining pull request information"""
import abc
from github import Repository


class MiningModule(abc.ABC):
    """
    This class is an abstract base class. All modules should inherit from this class. This class
    also contains a class variable, repo. Since all child classes will use the same repo, they
    can access that repo here.
    """

    repo: Repository.Repository = None

    @abc.abstractmethod
    def mine(self):
        """The mine method that each child should implement"""

    def get_repo(self):
        """
        Returns the repository that is mined. This method mainly exists because pylist enforces
        to have at least 2 public methods.
        """
        return self.repo
