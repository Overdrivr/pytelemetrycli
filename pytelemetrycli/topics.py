class Topics:
    def __init__(self):
        self.topics = dict()
        self.transfers = dict()

    def process(self,topic, payload):
        if not topic in self.topics:
            self.topics[topic] = []
        self.topics[topic].append(payload)
        # If there is an active transfer, transfer received data to the queue
        if topic in self.transfers:
            self.transfers[topic]['queue'].put([self.transfers[topic]['lastindex'], payload])
            self.transfers[topic]['lastindex'] += 1

    def ls(self):
        return self.topics.keys()

    def samples(self,topic,amount=1):
        if not topic in self.topics:
            return None
        if amount == 0 or amount is None:
            return self.topics[topic]
        return self.topics[topic][-amount:]

    def count(self,topic):
        if not topic in self.topics:
            return 0
        return len(self.topics[topic])

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
                for item in self.topics[topic]:
                    queue.put([self.transfers[topic]['lastindex'], item])
                    self.transfers[topic]['lastindex'] += 1
