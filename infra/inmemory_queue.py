import heapq
from multiprocessing import heap


class InMemoryQueue:
    def __init__(self):
        self.heap = []  
    
    def enqueue(self, item):
        heapq.heappush(self.heap, (item.due_time, item))

    def dequeue(self):
        if self.heap:
            return heapq.heappop(self.heap)
        return None, None

    def peek(self):
        if self.heap:
            return self.heap[0]
        return None, None