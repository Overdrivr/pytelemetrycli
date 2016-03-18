from sortedcontainers import SortedDict
from logging import getLogger

class Topic:
    """
A class to store and manage all data under a given topic
    """
    def __init__(self, name, source='remote'):
        self.raw = []
        self.indexes = SortedDict()
        self.source = source
        self.name = name

    def has_indexed_data(self):
        return len(self.indexes) > 0

    def new_sample(self, sample, options):
        if options:
            self.indexes[options['index']] = sample
        else:
            self.raw.append(sample)

class Topics:
    """
A class that manages a collection of `Topic`s.

    """
    def __init__(self):
        self.topic_list = SortedDict()
        self.transfers = dict()
        self.logger = getLogger('topics')
        self.logger.info('started session')

    def clear(self):
        self.logger.info('Cleared all topics and received data')
        self.topic_list = dict()
        self.transfers = dict()

    def create(self, topic, source='remote'):
        # Create the topic if it doesn't exist already
        if not topic in self.topic_list:
            self.topic_list[topic] = Topic(topic,source=source)
            self.logger.info('new:topic ' + topic)

    def process(self, topic, payload, options=None):
        # Create the topic if it doesn't exist already
        self.create(topic)

        # Add the new sample
        self.topic_list[topic].new_sample(payload,options)

        # logging
        if options:
            self.logger.debug('new sample | {0} [{1}] {2}'.format(topic, options['index'], payload))
        else:
            self.logger.debug('new sample | {0} {1}'.format(topic, payload))

        # If there is an active transfer, transfer received data to the queue
        if topic in self.transfers:
            # If transfer requires indexed data, check there is an index
            if self.transfers[topic]['type'] == 'indexed' and options is not None:
                x = options['index']
                self.transfers[topic]['queue'].put([x, payload])
            # For linear data, provide sample id for x and payload for y
            elif self.transfers[topic]['type'] == 'linear':
                x = self.transfers[topic]['lastindex']
                self.transfers[topic]['queue'].put([x, payload])
                self.transfers[topic]['lastindex'] += 1

    def ls(self,source="remote"):
        if source is None:
            return [t.name for t in self.topic_list.keys()]
        else:
            return [t.name for t in self.topic_list.values() if t.source == source]

    def samples(self,topic,amount=1):
        if not topic in self.topic_list:
            return None

        if amount == 0 or amount is None:
            return self.topic_list[topic].raw

        return self.topic_list[topic].raw[-amount:]

    def count(self,topic):
        if not topic in self.topic_list:
            return 0

        return len(self.topic_list[topic].raw)

    def exists(self,topic):
        return topic in self.topic_list

    def transfer(self, topic, queue, transfer_type = "linear"):
        # If the topic data is not already transfered to some queue
        if not topic in self.transfers:
            self.transfers[topic] = dict()
            self.transfers[topic]['queue'] = queue
            self.transfers[topic]['lastindex'] = 0
            self.transfers[topic]['type'] = transfer_type

            self.logger.info('start transfer | {0}'.format(topic))

            # If there is already existing data under the topic
            if topic in self.topic_list:
                if transfer_type == 'indexed':
                    for key, value in self.topic_list[topic].indexes.iteritems():
                        queue.put([key, value])
                elif transfer_type == 'linear':
                    for item in self.topic_list[topic].raw:
                        queue.put([self.transfers[topic]['lastindex'], item])
                        self.transfers[topic]['lastindex'] += 1

    def untransfer(self,topic):
        # If the topic data is already transfered to some queue
        if topic in self.transfers:
            # Remove it from the transfer list
            del self.transfers[topic]
            self.logger.info('stop transfer | {0}'.format(topic))

    def intransfer(self,topic):
        return topic in self.transfers

    def xytype(self,topic):
        return self.topic_list[topic]['type']
