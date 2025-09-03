import heapq

from infra.models.enqueue_item import EnqueueItem


class InMemoryQueue:
    def __init__(self):
        self.heap = []  
    
    def enqueue(self, item: EnqueueItem):
        heapq.heappush(self.heap, (item.due_time, item))

    def dequeue(self) -> tuple[float, EnqueueItem] | tuple[None, None]:
        if self.heap:
            return heapq.heappop(self.heap)
        return None, None

    def peek(self):
        if self.heap:
            return self.heap[0]
        return None, None