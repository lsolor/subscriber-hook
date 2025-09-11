import heapq
import threading
from app.infra.models.enqueue_item import EnqueueItem
import logging

logger = logging.getLogger(__name__)

class InMemoryQueue:
    """
    Thread-safe min-heap priority queue ordered by (due_time, seq).
    Externally returns (due_time, item) to keep callers simple.
    """

    def __init__(self):
        self._heap: list[tuple[float, int, EnqueueItem]] = []
        self._lock = threading.Lock()
        self._seq = 0
        self.dlq = []

    def _next_seq(self) -> int:
        self._seq += 1
        return self._seq

    def enqueue(self, item: EnqueueItem, *, due_time: float | None = None) -> None:
        if due_time is None:
            if not hasattr(item, "due_time"):
                raise ValueError("enqueue requires due_time or item.due_time")
            due_time = float(item.due_time)
        with self._lock:
            seq = self._next_seq()
            heapq.heappush(self._heap, (float(due_time), seq, item))

    def dequeue(self, now) -> EnqueueItem | None:
        with self._lock:
            if not self._heap:
                return None
            head_due, _, _ = self._heap[0]
            if head_due > now:
                return None
            due_time, _seq, item = heapq.heappop(self._heap)
            return item
    

    def to_dlq(self,item,reason):
        self.dlq.append((item,reason))

    def peek(self) -> tuple[float, EnqueueItem] | tuple[None, None]:
        with self._lock:
            if not self._heap:
                return None, None
            due_time, _seq, item = self._heap[0]
            return due_time, item

    def __len__(self) -> int:
        with self._lock:
            return len(self._heap)
