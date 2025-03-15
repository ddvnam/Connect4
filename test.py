class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
    
    def reverse(self):
        prev, current = None, self.head
        while current:
            current.next = prev
            prev = current
            current = current.next
        self.head = prev