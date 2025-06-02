from dataclasses import dataclass, field

@dataclass
class IdObj:
    raw: any  
    prefix: str
    position: int
    type: str  
    other_type: str = ""
    prev : str = ""
    
    value: str = field(init=False)
    
    def __post_init__(self):
        self.value = f"{self.prefix}{self.raw}"
    
    def get_value(self) -> str:
        return self.value

    def get_raw(self):
        return self.raw

    def get_prefix(self) -> str:
        return self.prefix

    def get_position(self) -> int:
        return self.position

    def get_type(self) -> str:
        return self.type

    def get_other_type(self) -> str:
        return self.other_type


