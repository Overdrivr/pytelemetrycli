from sortedcontainers import SortedDict
from logging import getLogger

class Topics:
    def __init__(self):
        self.topics = dict()
        self.transfers = dict()
        self.logger = getLogger('topics')
        self.logger.info('started session')

    def process(self,topic, payload, options=None):
        if not topic in self.topics:
            self.topics[topic] = dict()
            self.topics[topic]['raw'] = [] # For raw data
            self.topics[topic]['xy'] = SortedDict() # For indexed data
            if options:
                self.topics[topic]['type'] = 'indexed'
                self.logger.info('new:topic:indexed ' + topic)
            else:
                self.topics[topic]['type'] = 'linear'
                self.logger.info('new:topic:linear ' + topic)

        t = self.topics[topic]
        t['raw'].append(payload)

        if options:
            self.logger.debug('new sample | {0} [{1}] {2}'.format(topic, options['index'], payload))
        else:
            self.logger.debug('new sample | {0} {1}'.format(topic, payload))

        # If topic is of type indexed data, also store in ordered dict
        if options:
            t['xy'][options['index']] = payload

        # If there is an active transfer, transfer received data to the queue
        if topic in self.transfers:
            # For indexed data, provide the index for x and payload for y
            if t['type'] == 'indexed' and options is not None:
                x = options['index']
                self.transfers[topic]['queue'].put([x, payload])
            # For linear data, provide sample id for x and payload for y
            elif t['type'] == 'linear':
                x = self.transfers[topic]['lastindex']
                self.transfers[topic]['queue'].put([x, payload])
                self.transfers[topic]['lastindex'] += 1
            else:
                self.logger.warning('unknown topic type {0} | {1}'.format(t['type'], topic))

    def ls(self):
        return sorted(self.topics.keys())

    def samples(self,topic,amount=1):
        if not topic in self.topics:
            return None
        if amount == 0 or amount is None:
            return self.topics[topic]['raw']
        # TODO : Print indexed data ?
        return self.topics[topic]['raw'][-amount:]

    def count(self,topic):
        if not topic in self.topics:
            return 0
        # TODO : what to do on indexed data ?
        return len(self.topics[topic]['raw'])

    def exists(self,topic):
        return topic in self.topics

    def transfer(self,topic,queue):
        # If the topic data is not already transfered to some queue
        if not topic in self.transfers:
            self.transfers[topic] = dict()
            self.transfers[topic]['queue'] = queue
            self.transfers[topic]['lastindex'] = 0

            self.logger.info('start transfer | {0}'.format(topic))

            # If there is already existing data under the topic
            if topic in self.topics:
                if self.topics[topic]['type'] == 'indexed':
                    for key, value in self.topics[topic]['xy'].iteritems():
                        queue.put([key, value])
                elif self.topics[topic]['type'] == 'linear':
                    for item in self.topics[topic]['raw']:
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
        return self.topics[topic]['type']
