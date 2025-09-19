from enum import Enum, EnumMeta
from typing import List, Tuple


class ChoicesMeta(EnumMeta):
    def __getattribute__(cls, name):
        attr = super().__getattribute__(name)
        
        # ? Обрабатываем только таплы определенного размера
        # * Пародия choices как в django
        # | https://github.com/django/django/blob/main/django/db/models/enums.py
        if (isinstance(attr, tuple) and 
            len(attr) == 2 and 
            isinstance(attr[0], (int, str)) and 
            isinstance(attr[1], int)):
            return attr[0]
        
        return attr
    
class Choices(Enum, metaclass=ChoicesMeta):
    def __new__(cls, value: str, label: str):
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.label = label
        return obj
    
    
    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(member.value, member.label) for member in cls]
    
    @classmethod
    def get_label(cls, value: str) -> str:
        for member in cls:
            if member.value == value:
                return member.label
    
    
    @classmethod
    def get_value(cls, label: str) -> str:
        for member in cls:
            if member.label == label:
                return member.value
    
class TextChoices(str, Choices):
    pass