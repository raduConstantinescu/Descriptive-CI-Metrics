import abc

from github.Repository import Repository


class RepositoryAnalyzer:

    @abc.abstractmethod
    def analyze(self):
        """The analyze method that each child should implement"""
