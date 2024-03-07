from queue import Queue


class Buffer(Queue):

    def put(self, item, block=True, timeout=None):
        # Drop oldest element if queue is full
        if self.full():
            self.get_nowait()

        return Queue.put(self, item, block, timeout)

    def stream(self):
        while True:
            yield self.get()