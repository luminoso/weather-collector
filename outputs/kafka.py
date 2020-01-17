import logging
from json import dumps

from kafka import KafkaProducer

from utils.genericOutput import GenericOutput
from utils.genericSource import GenericSource


class kafkaproducer(GenericOutput):
    """
    Sends the sources results to a kafka server
    """

    def __init__(self, address):
        super().__init__()
        self.kafka_server = address
        self.kafka_producer = KafkaProducer(bootstrap_servers=[address],
                                            value_serializer=lambda x: dumps(x).encode('utf-8'))

    def write(self, source: GenericSource):

        # statistics if kafka is receiving the messages without errors
        stats = {
            "errors": 0,
            "successes": 0,
            "min_offset": None,
            "max_offset": None,
            "errorTypes": {}
        }

        # add a callback for kafka process
        def errback_listener(error, **kargs):
            if type(error).__name__ not in kargs["stats"]["errorTypes"]:
                kargs["stats"]["errorTypes"][type(error).__name__] = 0
            kargs["stats"]["errorTypes"][type(error).__name__] += 1
            kargs["stats"]["errors"] += 1

        # send all messages we have in queue
        for msg in source:
            future = self.kafka_producer.send(topic=source.name, value=msg)
            future.add_errback(errback_listener, stats=stats)

        # make sure they're all sent
        self.kafka_producer.flush()

        # check if any sent message failed
        if stats['errors'] > 0:
            logging.getLogger().warning(f'Failing to send {source.name}. Lost messages: {stats["errors"]}')