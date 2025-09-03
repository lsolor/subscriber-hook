

class EnqueueItem:
    def __init__(self, event_id: int, event_type: str, data: dict, due_time: float = 0.0, correlation_id: str = None, endpoint_url: str = None, max_attempts: int = 4):
        self.event_id = event_id
        self.event_type = event_type
        self.data = data
        self.due_time = due_time
        self.correlation_id = correlation_id
        self.endpoint_url = endpoint_url
        self.attempts = 1  # Number of delivery attempts
        self.max_attempts = max_attempts
