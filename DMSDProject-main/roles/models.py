from common.utils import JsonSerializable


class Role(JsonSerializable):
    def __init__(self, name: str, description = '', is_active = 1):
        self.name = name
        self.description = description
        self.is_active = 1 if is_active else 0
    