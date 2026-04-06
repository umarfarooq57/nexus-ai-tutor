"""
NEXUS AI Tutor - Agentic AI Framework
Autonomous AI agents for intelligent tutoring
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
import json
import uuid

logger = logging.getLogger('nexus.agents')


class AgentRole(Enum):
    """Roles for AI agents"""
    TUTOR = "tutor"
    RESEARCHER = "researcher"
    EVALUATOR = "evaluator"
    PLANNER = "planner"
    CODER = "coder"
    EXPLAINER = "explainer"
    REVIEWER = "reviewer"


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentMessage:
    """Message between agents or user"""
    role: str  # 'user', 'agent', 'system'
    content: str
    agent_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AgentAction:
    """Action taken by an agent"""
    action_type: str
    description: str
    parameters: Dict
    result: Optional[Any] = None
    success: bool = True
    error: Optional[str] = None


@dataclass
class AgentThought:
    """Agent's reasoning step"""
    thought: str
    action: Optional[AgentAction] = None
    observation: Optional[str] = None


class Tool:
    """Base class for agent tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    async def execute(self, **kwargs) -> Any:
        raise NotImplementedError


class SearchTool(Tool):
    """Search knowledge base"""
    
    def __init__(self):
        super().__init__(
            "search_knowledge",
            "Search the knowledge base for relevant information on a topic"
        )
    
    async def execute(self, query: str, **kwargs) -> Dict:
        # Would integrate with vector DB
        return {
            "results": [
                {"title": "Introduction to the topic", "relevance": 0.95},
                {"title": "Advanced concepts", "relevance": 0.82}
            ],
            "total": 2
        }


class CodeExecutionTool(Tool):
    """Execute code in sandbox"""
    
    def __init__(self):
        super().__init__(
            "execute_code",
            "Execute Python code in a safe sandbox and return output"
        )
    
    async def execute(self, code: str, language: str = "python", **kwargs) -> Dict:
        # Would use code sandbox
        return {
            "output": "Code executed successfully",
            "execution_time": 0.5,
            "success": True
        }


class QuizGeneratorTool(Tool):
    """Generate quiz questions"""
    
    def __init__(self):
        super().__init__(
            "generate_quiz",
            "Generate quiz questions on a topic"
        )
    
    async def execute(self, topic: str, num_questions: int = 5, **kwargs) -> Dict:
        return {
            "questions": [
                {"question": f"Question about {topic}", "type": "mcq"}
                for _ in range(num_questions)
            ]
        }


class DiagramAnalyzerTool(Tool):
    """Analyze diagrams and images"""
    
    def __init__(self):
        super().__init__(
            "analyze_diagram",
            "Analyze an educational diagram and explain its components"
        )
    
    async def execute(self, image_data: str, **kwargs) -> Dict:
        return {
            "components": ["Component A", "Component B"],
            "relationships": [{"from": "A", "to": "B", "type": "connects"}],
            "explanation": "This diagram shows..."
        }


class Agent:
    """
    Autonomous AI Agent
    Uses ReAct (Reasoning + Acting) pattern
    """
    
    def __init__(
        self,
        agent_id: str,
        role: AgentRole,
        name: str,
        system_prompt: str,
        tools: List[Tool] = None,
        config: Dict = None
    ):
        self.agent_id = agent_id
        self.role = role
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools or []
        self.config = config or {}
        self.status = AgentStatus.IDLE
        self.memory: List[AgentMessage] = []
        self.thoughts: List[AgentThought] = []
        self.max_iterations = config.get('max_iterations', 10)
    
    def get_tool_descriptions(self) -> str:
        """Format tool descriptions for prompt"""
        if not self.tools:
            return "No tools available."
        
        descriptions = []
        for tool in self.tools:
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)
    
    async def think(self, context: str) -> AgentThought:
        """
        Generate a thought/reasoning step
        Uses ReAct pattern: Thought -> Action -> Observation
        """
        from services.llm import llm_service
        
        tools_desc = self.get_tool_descriptions()
        
        prompt = f"""You are {self.name}, a {self.role.value} agent.

{self.system_prompt}

Available Tools:
{tools_desc}

Current Context:
{context}

Previous Thoughts:
{self._format_thoughts()}

Think step by step. What should you do next?
Format your response as:
THOUGHT: Your reasoning
ACTION: tool_name(param1="value1", param2="value2") OR "respond" if ready to give final answer
"""
        
        response = await llm_service.generate(prompt, temperature=0.7)
        
        # Parse response
        thought = self._parse_thought(response.content)
        self.thoughts.append(thought)
        
        return thought
    
    def _format_thoughts(self) -> str:
        """Format previous thoughts for context"""
        if not self.thoughts:
            return "None yet."
        
        formatted = []
        for i, t in enumerate(self.thoughts[-5:]):  # Last 5 thoughts
            formatted.append(f"{i+1}. Thought: {t.thought}")
            if t.action:
                formatted.append(f"   Action: {t.action.action_type}")
            if t.observation:
                formatted.append(f"   Observation: {t.observation[:200]}")
        
        return "\n".join(formatted)
    
    def _parse_thought(self, response: str) -> AgentThought:
        """Parse LLM response into thought structure"""
        thought_text = ""
        action = None
        
        lines = response.split('\n')
        for line in lines:
            if line.startswith('THOUGHT:'):
                thought_text = line.replace('THOUGHT:', '').strip()
            elif line.startswith('ACTION:'):
                action_str = line.replace('ACTION:', '').strip()
                if action_str != 'respond':
                    action = self._parse_action(action_str)
        
        return AgentThought(thought=thought_text, action=action)
    
    def _parse_action(self, action_str: str) -> Optional[AgentAction]:
        """Parse action string into AgentAction"""
        try:
            # Extract tool name and parameters
            if '(' in action_str:
                tool_name = action_str.split('(')[0].strip()
                params_str = action_str.split('(')[1].rstrip(')')
                
                # Simple parameter parsing
                params = {}
                if params_str:
                    for param in params_str.split(','):
                        if '=' in param:
                            key, value = param.split('=', 1)
                            params[key.strip()] = value.strip().strip('"\'')
                
                return AgentAction(
                    action_type=tool_name,
                    description=f"Execute {tool_name}",
                    parameters=params
                )
        except Exception as e:
            logger.error(f"Error parsing action: {e}")
        
        return None
    
    async def execute_action(self, action: AgentAction) -> str:
        """Execute an action using tools"""
        for tool in self.tools:
            if tool.name == action.action_type:
                try:
                    self.status = AgentStatus.EXECUTING
                    result = await tool.execute(**action.parameters)
                    action.result = result
                    action.success = True
                    return json.dumps(result)
                except Exception as e:
                    action.success = False
                    action.error = str(e)
                    return f"Error: {e}"
        
        return f"Tool '{action.action_type}' not found"
    
    async def run(self, task: str, context: Dict = None) -> str:
        """
        Run the agent on a task
        Uses ReAct loop: Think -> Act -> Observe -> Repeat
        """
        self.status = AgentStatus.THINKING
        self.thoughts = []
        
        full_context = f"Task: {task}"
        if context:
            full_context += f"\nAdditional Context: {json.dumps(context)}"
        
        for iteration in range(self.max_iterations):
            # Think
            thought = await self.think(full_context)
            
            if thought.action is None:
                # Agent is ready to respond
                self.status = AgentStatus.COMPLETED
                return self._generate_final_response()
            
            # Act
            observation = await self.execute_action(thought.action)
            thought.observation = observation
            
            # Update context with observation
            full_context += f"\nObservation from {thought.action.action_type}: {observation}"
        
        self.status = AgentStatus.COMPLETED
        return self._generate_final_response()
    
    def _generate_final_response(self) -> str:
        """Generate final response based on thoughts and observations"""
        if not self.thoughts:
            return "I couldn't process this request."
        
        # Combine insights from all thoughts
        insights = [t.thought for t in self.thoughts if t.thought]
        observations = [t.observation for t in self.thoughts if t.observation]
        
        return f"Based on my analysis:\n\n" + "\n".join(insights[-3:])


class TutorAgent(Agent):
    """Specialized tutor agent for teaching"""
    
    def __init__(self, subject: str = "general"):
        super().__init__(
            agent_id=f"tutor_{uuid.uuid4().hex[:8]}",
            role=AgentRole.TUTOR,
            name=f"Professor AI ({subject})",
            system_prompt=f"""You are an expert tutor specializing in {subject}.
Your goal is to help students understand concepts deeply.
- Break down complex topics into simple parts
- Use examples and analogies
- Encourage questions
- Check for understanding""",
            tools=[
                SearchTool(),
                CodeExecutionTool(),
                QuizGeneratorTool(),
                DiagramAnalyzerTool()
            ]
        )
        self.subject = subject


class CodeReviewAgent(Agent):
    """Specialized agent for code review"""
    
    def __init__(self):
        super().__init__(
            agent_id=f"reviewer_{uuid.uuid4().hex[:8]}",
            role=AgentRole.REVIEWER,
            name="Code Review AI",
            system_prompt="""You are an expert code reviewer.
- Check for bugs and errors
- Suggest improvements
- Follow best practices
- Explain issues clearly""",
            tools=[
                CodeExecutionTool(),
                SearchTool()
            ]
        )


class MultiAgentOrchestrator:
    """
    Orchestrates multiple agents for complex tasks
    """
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.conversations: Dict[str, List[AgentMessage]] = {}
    
    def register_agent(self, agent: Agent):
        """Register an agent"""
        self.agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")
    
    def create_tutor_agent(self, subject: str) -> Agent:
        """Create and register a tutor agent"""
        agent = TutorAgent(subject)
        self.register_agent(agent)
        return agent
    
    async def route_to_agent(self, message: str, context: Dict = None) -> tuple:
        """
        Route a message to the appropriate agent
        Returns (agent_id, response)
        """
        # Determine best agent based on message content
        agent = self._select_agent(message, context)
        
        if agent is None:
            # Create default tutor
            agent = self.create_tutor_agent("general")
        
        response = await agent.run(message, context)
        
        return agent.agent_id, response
    
    def _select_agent(self, message: str, context: Dict = None) -> Optional[Agent]:
        """Select the best agent for the message"""
        message_lower = message.lower()
        
        # Simple keyword-based routing
        if any(kw in message_lower for kw in ['code', 'debug', 'error', 'function']):
            for agent in self.agents.values():
                if agent.role == AgentRole.REVIEWER:
                    return agent
        
        if any(kw in message_lower for kw in ['explain', 'teach', 'learn', 'understand']):
            for agent in self.agents.values():
                if agent.role == AgentRole.TUTOR:
                    return agent
        
        # Return any available agent
        if self.agents:
            return list(self.agents.values())[0]
        
        return None
    
    async def collaborative_solve(
        self,
        task: str,
        agent_roles: List[AgentRole]
    ) -> Dict[str, Any]:
        """
        Multiple agents collaborate to solve a task
        """
        results = {}
        context = {"task": task, "previous_results": {}}
        
        for role in agent_roles:
            # Find or create agent for role
            agent = None
            for a in self.agents.values():
                if a.role == role:
                    agent = a
                    break
            
            if agent is None:
                if role == AgentRole.TUTOR:
                    agent = self.create_tutor_agent("general")
                elif role == AgentRole.REVIEWER:
                    agent = CodeReviewAgent()
                    self.register_agent(agent)
            
            if agent:
                response = await agent.run(task, context)
                results[role.value] = response
                context["previous_results"][role.value] = response
        
        return results


# Global orchestrator instance
orchestrator = MultiAgentOrchestrator()

# Pre-register common agents
orchestrator.register_agent(TutorAgent("Machine Learning"))
orchestrator.register_agent(TutorAgent("Python Programming"))
orchestrator.register_agent(CodeReviewAgent())
