"""Module for mining topics from a repository."""
import dataclasses
from modules.mining_module import MiningModule

@dataclasses.dataclass
class TopicsModule(MiningModule):
    """
    This class mines topics from a repository

    Attributes
    ----------
    topics : list
        A list of topics from the repository
    json : dict
        Dictionary containing information about the topics

    Methods
    -------
    mine()
        The main entry point to this class. Calling this function will mine all the data in the body
    """
    def __init__(self):
        print(f"Extracting topics data for repo {super().repo.full_name}")
        self.topics = super().repo.get_topics()

        self.json = {'topics': self.topics}

    def mine(self):
        """Returns a dictionary with all the mined data"""
        return self.json
