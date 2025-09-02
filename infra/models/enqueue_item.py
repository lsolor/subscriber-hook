

class EnqueueItem:
    def __init__(self, event_id: int, event_type: str, data: dict, due_time: int = 0, correlation_id: str = None, endpoint_url: str = None):
        self.event_id = event_id
        self.event_type = event_type
        self.data = data
        self.due_time = due_time
        self.correlation_id = correlation_id
        self.endpoint_url = endpoint_url
        self.attempts = 0  # Number of delivery attempts

    def __lt__(self, other):
        if self.due_time == other.due_time:
            return self.correlation_id < other.correlation_id
        return self.due_time < other.due_time