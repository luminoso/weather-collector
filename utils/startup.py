import importlib
import logging
from json import dumps
from typing import List, Callable

import yaml
from kafka import KafkaProducer
from yaml.parser import ParserError

from .exit_codes import *
from .genericSource import GenericSource


def read_args_and_config():
    """
    Defines command line arguments
    Parses arguments if any
    Simple configuration file validation
    :return:
    """
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="./config.yaml", help="Config file")
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    args = parser.parse_args()

    # validate config file basic syntax and existence
    try:
        with open(args.config) as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
    except ParserError:
        print("Config file isn't a valid yaml file")
        exit(INVALID_YAML)
    except FileNotFoundError:
        print(f"Config file not found: {args.config}")
        exit(CONFIG_NOT_FOUND)

    # validate verbosity config
    if config.get('verbosity'):

        available_levels = logging._nameToLevel.keys()

        if config['verbosity'] not in available_levels:
            print(f'Set config verbosity level to one of the following: {[x for x in available_levels]}')
            exit(WRONG_VERBOSITY_CONFIG)

    # validate refresh rate config
    try:
        int(config['refresh_rate_minutes'])
    except ValueError:
        print(f"Invalid refresh rate value: {config['refresh_rate_minutes']}")
        exit(INVALID_REFRESH_RATE_VAL)
    except KeyError:
        print(f"'refresh_rate_minutes' not found in config file")
        exit(REFRESH_RATE_NOT_FOUND)

    # validate output
    if not config.get('output'):
        print(f'No output configured, so nothing to do')
        exit(NO_OUTPUT_FOUND)

    # finished some very basic config validation

    return config


def instanciate_logging(config: dict):
    """
    Configures the logging system
    :param config: to read configurations from
    """
    verbosity_level = 'FATAL'

    if config.get('verbosity'):
        verbosity_level = config['verbosity']

    logging.basicConfig(
        level=logging._nameToLevel[verbosity_level],
        format="%(asctime)s [%(module)-12.12s] [%(levelname)-5.5s]  %(message)s",
        # format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
        handlers=[
            logging.StreamHandler()
        ])

    logging.info(f"Set verbosity to {logging.getLevelName(logging.getLogger().getEffectiveLevel())}")


def instanciate_sources(modules: dict) -> List[GenericSource]:
    """
    Creates sources based on the config file where each key is a module and each subkey is a class
    Each class can also have custom configurations when creating an instance
    :param modules: dictionary with modules/classes to create
    :return: list of instances of classes
    """
    classes_instantiated = []

    for module in modules.keys():

        # import python module
        pmodule = importlib.import_module(f'{module}.{module}')

        # each source in the module may have configurations
        for source, params in modules[module].items():

            # create a class from the module
            class_ = getattr(pmodule, source)

            if params:
                # specific module config
                instance = class_(params['enabled'])
            else:
                instance = class_()

            classes_instantiated.append(instance)

    return classes_instantiated


def instanciate_outputs(config: dict) -> List[Callable]:
    """
    Defines ouput functions that are invoked for each one of the sources
    :param config: config file
    :return: list with output functions
    """
    outputs = []

    if config.get('console'):
        # create a very dummy output
        def print_to_console(source: GenericSource):
            logging.info(f'Retrieved {len(source)} items from {source.name}')

        outputs.append(print_to_console)

    if config.get('writefiles'):
        def write_to_file(source: GenericSource):
            """
            Stub that writes messages to a file and a new line on the end
            :param source: source with messages to write
            """

            filename = f'{source.name}.txt'

            logging.debug(f'Writing {len(source)} messages to file {filename}')

            for msg in source:
                with open(filename, "a") as myfile:
                    myfile.write(str(msg))

                with open(filename, "a") as myfile:
                    myfile.write('\n')

        outputs.append(write_to_file)

    if config.get('kafka'):

        kafka_server = config['kafka']['address']

        kafka_producer = KafkaProducer(bootstrap_servers=[kafka_server],
                                       value_serializer=lambda x: dumps(x).encode('utf-8'))

        def send_to_kafka(source: GenericSource):

            for msg in source:
                kafka_producer.send(topic=source.name, value=msg)

        outputs.append(send_to_kafka)

    return outputs
