class Topics:
    def __init__(self, telemetry):
        self.topics = dict()
        self.telemetry = telemetry
        telemetry.subscribe(None,self.process)

    def process(self,topic, payload):
        if not topic in self.topics:
            self.topics[topic] = []
        self.topics[topic].append(payload)

    def ls(self):
        return self.topics.keys()

    def samples(self,topic,amount=1):
        if not topic in self.topics:
            return None
        return self.topics[topic][-amount:]

    def count(self,topic):
        if not topic in self.topics:
            return 0
        return count(self.topics[topic])
