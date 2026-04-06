# Agents service package
from .agent_framework import (
    Agent,
    AgentRole,
    AgentStatus,
    AgentMessage,
    AgentAction,
    AgentThought,
    Tool,
    MultiAgentOrchestrator,
    orchestrator
)
from .teaching_agents import (
    MLTutorAgent,
    PythonTutorAgent,
    MathTutorAgent,
    DataScienceTutorAgent,
    DevOpsTutorAgent,
    SocraticTutorAgent,
    TeachingAgentFactory
)

__all__ = [
    'Agent',
    'AgentRole',
    'AgentStatus',
    'AgentMessage',
    'AgentAction',
    'AgentThought',
    'Tool',
    'MultiAgentOrchestrator',
    'orchestrator',
    'MLTutorAgent',
    'PythonTutorAgent',
    'MathTutorAgent',
    'DataScienceTutorAgent',
    'DevOpsTutorAgent',
    'SocraticTutorAgent',
    'TeachingAgentFactory'
]
