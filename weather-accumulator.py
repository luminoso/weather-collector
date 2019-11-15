import time
from typing import List

from utils.genericSource import GenericSource


def main(sources: List[GenericSource], outputs: list, refresh_rate_min: int):
    running = True
    while running:

        for source in sources:

            try:
                # refresh the source
                source.refresh_source()

                # calculate just the incremental change since last refresh
                source.calculate_incremental()
            except Exception as e:
                logging.fatal(f'Exception during {source.name} refresh')
                print(e)

            for output in outputs:
                try:
                    # checks if source has new data since last call
                    if source:
                        output(source)
                    else:
                        logging.debug(f"{source.name} has no new items")

                except Exception as e:
                    logging.fatal(f'Exception while sending {source.name} to output {output}')
                    logging.debug(e)

        time.sleep(refresh_rate_min * 60)


if __name__ == "__main__":

    from kafka.errors import NoBrokersAvailable
    from utils.startup import *

    # check command line and config file
    config = read_args_and_config()

    # configure logging
    instanciate_logging(config)

    # check which sources to pull, import modules, create classes
    sources = instanciate_sources(config['sources'])
    try:
        sources = instanciate_sources(config['sources'])
    except Exception as e:
        # many things can go wrong here
        print("Can't instantiate all sources")
        print(e)
        exit(SOURCES_CLASSES_CREATION_ERROR)

    # create outputs. this may fail due to some kafka unavailability
    try:
        outputs = instanciate_outputs(config['output'])
    except NoBrokersAvailable:
        print("Kafka broker not reachable.")
        exit(KAFKA_BROKER_NOT_FOUND)

    try:
        # collect from sources to the outputs every X minutes
        # noinspection PyUnboundLocalVariable
        main(sources, outputs, config['refresh_rate_minutes'])
    except KeyboardInterrupt:
        logging.info(f"Exiting...")
