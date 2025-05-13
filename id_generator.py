import uuid
import random

class IdGenerator:
    def __init__(self, prefix="ID_", start=100000000, end=999999999):
        self.prefix = prefix
        self.start = start
        self.end = end
        self.current_id = start -1

    def generate_id(self):
        if self.current_id < self.end:
            self.current_id+=1
            return f"{self.prefix}{self.current_id}"
        else:
            raise ValueError("ID limit reached")

    @staticmethod
    def generate_uuid():
        return str(uuid.uuid4())

