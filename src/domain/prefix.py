
import json

class Prefix:
    
    def __init__(self, json_file):
        self.json_file = json_file
        self.prefixes = self.load_prefixes()
    
    def load_prefixes(self):
        try:
            with open(self.json_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            raise ValueError("Error: Unable to load prefix data.")
    
    def get_prefix(self, key):
        return self.prefixes.get(key, "")

