class Queue(object):
    def __init__(self):
        self.queue = []

    def enqueue(self,object):
        self.queue.append(object)

    def dequeue(self):
        if not len(self.queue):
            return None
        else:
            return self.queue.pop()
    
    def get_queue(self):
        return self.queue

        