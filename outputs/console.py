import logging

from utils.genericOutput import GenericOutput
from utils.genericSource import GenericSource


class console_output_stats(GenericOutput):
    """
    Prints source statistics to console
    """

    def write(self, source: GenericSource):
        logging.info(f'Retrieved {len(source)} items from {source.name}')