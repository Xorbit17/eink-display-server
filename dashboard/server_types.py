from abc import ABC, abstractmethod
import json
from typing import Tuple

RGB = Tuple[int, int, int]

class BaseLogger(ABC):
    @abstractmethod
    def debug(self,msg,**ctx) -> None:
        """Subclasses must implement this"""
        pass
    def info(self,msg,**ctx) -> None:
        """Subclasses must implement this"""
        pass
    def warn(self,msg,**ctx) -> None:
        """Subclasses must implement this"""
        pass
    def error(self,msg,**ctx) -> None:
        """Subclasses must implement this"""
        pass

class ConsoleLogger(BaseLogger):
    def debug(self, msg: str, **ctx ) -> None:
        print(f"[DEBUG] {msg}", json.dumps(ctx) if  ctx else "")

    def info(self, msg: str, **ctx ) -> None:
        print(f"[INFO] {msg}", json.dumps(ctx) if  ctx else "")

    def warn(self, msg: str, **ctx ) -> None:
        print(f"[WARN] {msg}", json.dumps(ctx) if  ctx else "")

    def error(self, msg: str, **ctx ) -> None:
        print(f"[ERROR] {msg}", json.dumps(ctx) if  ctx else "")
