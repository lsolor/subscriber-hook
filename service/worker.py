# own enqueue/ dequeue implementation and backoff logic for retries

class Worker:
    def __init__(self, queue, processor):
        self.queue = queue
        self.processor = processor

    def start(self):
        while True:
            item = self.queue.dequeue()
            if item:
                self.processor.process(item)

    def enqueue(self, item):
        self.queue.enqueue(item)

