from abc import ABC, abstractmethod

__all__ = [
    "Controller",
    ]

class Controller(ABC):
    @abstractmethod
    def func():
        pass

