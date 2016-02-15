from sortedcontainers import SortedDict

class Topics:
    def __init__(self):
        self.topics = dict()
        self.transfers = dict()

    def process(self,topic, payload, options=None):
        if not topic in self.topics:
            self.topics[topic] = dict()
            self.topics[topic]['raw'] = [] # For raw data
            self.topics[topic]['xy'] = SortedDict() # For indexed data
            if options:
                self.topics[topic]['type'] = 'indexed'
            else:
                self.topics[topic]['type'] = 'linear'

        t = self.topics[topic]
        t['raw'].append(payload)

        # If topic is of type indexed data, also store in ordered dict
        if options:
            t['xy'][options['index']] = payload

        # If there is an active transfer, transfer received data to the queue
        if topic in self.transfers:
            # For indexed data, provide the index for x and payload for y
            if t['type'] == 'indexed' and options is not None:
                self.transfers[topic]['queue'].put([options['index'], payload])
            # For linear data, provide sample id for x and payload for y
            elif t['type'] == 'linear':
                self.transfers[topic]['queue'].put([self.transfers[topic]['lastindex'], payload])
                self.transfers[topic]['lastindex'] += 1

    def ls(self):
        return self.topics.keys()

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
            # If there is already existing data under the topic
            if topic in self.topics:
                if self.topics[topic]['type'] == 'indexed':
                    for key, value in self.topics[topic]['xy'].iteritems():
                        queue.put([key, value])
                elif self.topics[topic]['type'] == 'linear':
                    for item in self.topics[topic]['raw']:
                        queue.put([self.transfers[topic]['lastindex'], item])
                        self.transfers[topic]['lastindex'] += 1
