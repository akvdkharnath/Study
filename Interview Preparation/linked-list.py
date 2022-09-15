
class Node(object):
    def __init__(self, data):
        self.data = data
        self.next = None


class Linkedlist(object):
    def __init__(self):
        self.head = None
    
    def insert_at_start(self, data):
        n = Node(data)
        n.next = self.head
        self.head = n
    
    def insert_at_end(self, data):
        n = Node(data)
        a = self.head
        while a is not None:
            a = a.next
        a.next = n

    def insert_after_selected_node(self, data, position):
        n = Node(data)
        a = self.head
        
        for i in range(1, position-1):
            a = a.next
        
        n.next = a.next 
        a.next = n
