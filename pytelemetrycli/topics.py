class Topics:
    def __init__(self):
        self.topics = dict()

    def process(self,topic, payload):
        if not topic in self.topics:
            self.topics[topic] = []
        self.topics[topic].append(payload)

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
