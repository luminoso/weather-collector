import logging

from utils.genericOutput import GenericOutput
from utils.genericSource import GenericSource

from json import dumps

class file_out(GenericOutput):
    """
    Writes output results to a file
    """

    def write(self, source: GenericSource):
        """
        Stub that writes messages to a file and a new line on the end
        :param source: source with messages to write
        """

        filename = f'{source.name}.txt'

        logging.debug(f'Writing {len(source)} messages to file {filename}')

        for msg in source:
            with open(filename, "a") as file:
                file.write(str(dumps(msg).encode('utf-8')))
                file.write('\n')
