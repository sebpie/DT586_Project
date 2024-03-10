from queue import Queue
from typing import Callable


class Buffer(Queue):

    def put(self, item, block=True, timeout=None):
        # Drop oldest element if queue is full
        if self.full():
            self.get_nowait()

        return Queue.put(self, item, block, timeout)

    def stream(self):
        while True:
            yield self.get()


class Subscribable(object):
    # subscribers: a lit of callback methods that consumers register.
    subscribers = []

    def subscribe(self, callback:Callable[[bytes], None]) -> None:
        self.subscribers.append(callback)

    def unsubscribe(self, callback:Callable[[bytes ], None]) -> None:
            self.subscribers.remove(callback)

    def publish(self, item):
        for callback in self.subscribers:
            callback(item)
