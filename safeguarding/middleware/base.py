# middleware/base.py
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

@dataclass
class FilterResult:
    text: str
    blocked: bool
    reason: Optional[str] = None


class LLMSafeguardMiddleware(ABC):
    """
    Abstract base class for all LLM safeguard middleware integrations.
    """

    @abstractmethod
    def process_input(self, text: str) -> FilterResult:
        """
        Process user input before sending to the LLM.
        Should return whether it's blocked and any modified text.
        """
        pass

    @abstractmethod
    def process_output(self, text: str) -> FilterResult:
        """
        Process LLM output before showing to the user.
        Should return whether it's blocked and any modified text.
        """
        pass
