import importlib
import logging

from typing import List, Callable

import yaml
from yaml.parser import ParserError

from .exit_codes import *
from .genericOutput import GenericOutput
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
    if not config.get('outputs'):
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


def instanciate_classes(modules: dict, module_root) -> List:
    """
    Creates sources based on the config file where each key is a module and each subkey is a class
    Each class can also have custom configurations when creating an instance
    :param modules: dictionary with modules/classes to create
    :return: list of instances of classes
    """
    classes_instantiated = []

    for module in modules.keys():

        # import python module
        pmodule = importlib.import_module(f'{module_root}.{module}')

        # each source in the module may have configurations
        for source, params in modules[module].items():

            # create a class from the module
            class_ = getattr(pmodule, source)

            if params:
                # specific module config
                instance = class_(**params)
            else:
                instance = class_()

            classes_instantiated.append(instance)

    return classes_instantiated


def instanciate_sources(dict) -> List[GenericSource]:
    return instanciate_classes(dict['sources'],'sources')


def instanciate_outputs(dict) -> List[GenericOutput]:
    return instanciate_classes(dict['outputs'], 'outputs')
