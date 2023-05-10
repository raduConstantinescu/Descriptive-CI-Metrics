"""Module for mining description information"""
import dataclasses
from modules.mining_module import MiningModule


@dataclasses.dataclass
class DescriptionModule(MiningModule):
    """
    This class mines description information
    
    Attributes
    ----------
    description : str
        The description of the repository
    json : dict
    Dictionary containing information about the description
        
    Methods
    -------
    mine()
        The main entry point to this class. Calling this function will mine all the data in the body
        
    """
    def __init__(self):
        self.description = super().repo.description
        if self.description is None:
            self.description = ""

        self.json = {'description': self.description}

    def mine(self):
        """Returns a dictionary with all the mined data"""
        return self.json
