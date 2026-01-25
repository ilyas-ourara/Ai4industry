"""
Base Agent class providing common functionality for all agents.
Follows object-oriented design principles.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from loguru import logger

from config import get_settings


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the multi-agent system.
    
    Provides common functionality:
    - Configuration management
    - Logging
    - State management
    - Error handling
    """

    def __init__(self, name: str, description: str = ""):
        """
        Initialize the base agent.
        
        Args:
            name: Unique identifier for the agent
            description: Human-readable description of agent's purpose
        """
        self.name = name
        self.description = description
        self.settings = get_settings()
        self._logger = logger.bind(agent=name)
        self._state: Dict[str, Any] = {}

    @property
    def logger(self):
        """Get the agent-specific logger."""
        return self._logger

    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """
        Main processing method to be implemented by each agent.
        
        Args:
            input_data: Input data specific to the agent type
            
        Returns:
            Processed output specific to the agent type
        """
        pass

    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data before processing.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if valid, raises exception otherwise
        """
        pass

    def update_state(self, key: str, value: Any) -> None:
        """Update the agent's internal state."""
        self._state[key] = value
        self.logger.debug(f"State updated: {key}")

    def get_state(self, key: str,    default: Any = None) -> Any:
        """Get a value from the agent's internal state."""
        return self._state.get(key, default)

    def clear_state(self) -> None:
        """Clear the agent's internal state."""
        self._state.clear()
        self.logger.debug("State cleared")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"

    def __str__(self) -> str:
        return f"Agent: {self.name} - {self.description}"
