from abc import ABC, abstractmethod
import json
from typing import Tuple
from dataclasses import dataclass

RGB = Tuple[int, int, int]

class BaseLogger(ABC):
    @abstractmethod
    def debug(self,msg,**ctx) -> None:
        """Subclasses must implement this"""
        pass

    @abstractmethod
    def info(self,msg,**ctx) -> None:
        """Subclasses must implement this"""
        pass

    @abstractmethod
    def warn(self,msg,**ctx) -> None:
        """Subclasses must implement this"""
        pass

    @abstractmethod
    def error(self,msg,**ctx) -> None:
        """Subclasses must implement this"""
        pass


@dataclass
class PrefixedLogger(BaseLogger):
    prefix: str
    wrapped: BaseLogger

    def debug(self,msg,**ctx) -> None:
        self.wrapped.debug(f"{self.prefix}{msg}",**ctx)

    def info(self,msg,**ctx) -> None:
        self.wrapped.info(f"{self.prefix}{msg}",**ctx)

    def warn(self,msg,**ctx) -> None:
        self.wrapped.warn(f"{self.prefix}{msg}",**ctx)

    def error(self,msg,**ctx) -> None:
        self.wrapped.debug(f"{self.prefix}{msg}",**ctx)

    
class ConsoleLogger(BaseLogger):
    def debug(self, msg: str, **ctx ) -> None:
        print(f"[DEBUG] {msg}", json.dumps(ctx) if  ctx else "")

    def info(self, msg: str, **ctx ) -> None:
        print(f"[INFO] {msg}", json.dumps(ctx) if  ctx else "")

    def warn(self, msg: str, **ctx ) -> None:
        print(f"[WARN] {msg}", json.dumps(ctx) if  ctx else "")

    def error(self, msg: str, **ctx ) -> None:
        print(f"[ERROR] {msg}", json.dumps(ctx) if  ctx else "")
