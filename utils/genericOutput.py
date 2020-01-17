from abc import abstractmethod

from utils.genericSource import GenericSource


class GenericOutput:
    """
    Defines an output
    """
    def __init__(self):
        super().__init__()
        # we use the class name as the source name
        self.name = self.__class__.__name__

    @abstractmethod
    def write(self, source: GenericSource):
        """
        Do something with source messages
        :param source: a generic source that has messages
        """

        # example
        for message in source:
            print(message)