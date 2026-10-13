"""
Deterministic mock adapter; external model providers are not implemented.
"""
from typing import Dict, Any, Optional
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Stewart Acid Base Sid Analyzer"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return f"[{self.system_name} mock]: No clinical analysis or external LLM inference performed. Input received: {prompt[:60]!r}."


class LLMFactory:
    """Creates the explicit mock adapter; unsupported providers raise an error."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Stewart Acid Base Sid Analyzer"):
        prov = str(provider).lower()
        if prov in ["mock", "deterministic", "test"]:
            return MockLLM(system_name)
        raise ValueError(f"Model provider {provider!r} is not implemented; only mock is supported.")
