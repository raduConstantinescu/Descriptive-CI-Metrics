import abc


class MiningModule(abc.ABC):
    @abc.abstractmethod
    def mine(self):
        pass
