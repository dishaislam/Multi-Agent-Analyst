from abc import ABC, abstractmethod
from typing import Dict, Any, List
from enum import Enum

class AgentType(Enum):
    DATA = "data"
    ANALYTICS = "analytics"
    CONVERSATIONAL = "conversational"
    REASONING = "reasoning"
    COORDINATOR = "coordinator"

class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, name: str, agent_type: AgentType):
        self.name = name
        self.agent_type = agent_type
        self.capabilities = []
        self.status = "idle"
    
    @abstractmethod
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task and return results"""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Return agent capabilities"""
        return self.capabilities
    
    def log(self, message: str, level: str = "INFO"):
        """Log agent activity"""
        print(f"[{self.name}] [{level}] {message}")
    
    def set_status(self, status: str):
        """Update agent status"""
        self.status = status
        self.log(f"Status changed to: {status}")