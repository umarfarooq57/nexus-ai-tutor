"""
NEXUS AI Tutor - LLM Integration Service
Provides unified interface to multiple LLM providers
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
import os

logger = logging.getLogger('nexus.llm')


@dataclass
class LLMResponse:
    """Response from LLM"""
    content: str
    model: str
    tokens_used: int
    finish_reason: str
    metadata: Dict[str, Any]


@dataclass
class Message:
    """Chat message"""
    role: str  # 'system', 'user', 'assistant'
    content: str


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        self.base_url = "https://api.openai.com/v1"
    
    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    **kwargs
                },
                timeout=60.0
            )
            
            data = response.json()
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=self.model,
                tokens_used=data.get("usage", {}).get("total_tokens", 0),
                finish_reason=data["choices"][0].get("finish_reason", "stop"),
                metadata=data
            )
    
    async def generate_stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        import httpx
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": True,
                    **kwargs
                },
                timeout=60.0
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            content = chunk["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str = None, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"
    
    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        import httpx
        
        # Extract system message
        system = ""
        chat_messages = []
        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                chat_messages.append({"role": m.role, "content": m.content})
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "max_tokens": max_tokens,
                    "system": system,
                    "messages": chat_messages,
                    **kwargs
                },
                timeout=60.0
            )
            
            data = response.json()
            
            return LLMResponse(
                content=data["content"][0]["text"],
                model=self.model,
                tokens_used=data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0),
                finish_reason=data.get("stop_reason", "stop"),
                metadata=data
            )
    
    async def generate_stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        # Simplified - would implement SSE streaming
        response = await self.generate(messages, temperature, max_tokens, **kwargs)
        yield response.content


class LocalLLMProvider(LLMProvider):
    """Local LLM provider (Ollama, vLLM, etc.)"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1"):
        self.base_url = base_url
        self.model = model
    
    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    },
                    "stream": False
                },
                timeout=120.0
            )
            
            data = response.json()
            
            return LLMResponse(
                content=data["message"]["content"],
                model=self.model,
                tokens_used=data.get("eval_count", 0),
                finish_reason="stop",
                metadata=data
            )
    
    async def generate_stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        import httpx
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": m.role, "content": m.content} for m in messages],
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    },
                    "stream": True
                },
                timeout=120.0
            ) as response:
                async for line in response.aiter_lines():
                    try:
                        data = json.loads(line)
                        content = data.get("message", {}).get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue


class LLMService:
    """
    Unified LLM Service
    Provides intelligent routing and fallback between providers
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available LLM providers"""
        
        # OpenAI
        if os.getenv('OPENAI_API_KEY'):
            self.providers['openai'] = OpenAIProvider()
            self.providers['gpt-4'] = OpenAIProvider(model='gpt-4')
            self.providers['gpt-3.5'] = OpenAIProvider(model='gpt-3.5-turbo')
        
        # Anthropic
        if os.getenv('ANTHROPIC_API_KEY'):
            self.providers['anthropic'] = AnthropicProvider()
            self.providers['claude-3-sonnet'] = AnthropicProvider(model='claude-3-sonnet-20240229')
            self.providers['claude-3-opus'] = AnthropicProvider(model='claude-3-opus-20240229')
        
        # Local
        self.providers['local'] = LocalLLMProvider()
        self.providers['llama'] = LocalLLMProvider(model='llama3.1')
        
        logger.info(f"Initialized LLM providers: {list(self.providers.keys())}")
    
    def get_provider(self, provider_name: str = None) -> LLMProvider:
        """Get a specific provider or default"""
        if provider_name and provider_name in self.providers:
            return self.providers[provider_name]
        
        # Default priority: GPT-4 > Claude > Local
        for name in ['gpt-4', 'claude-3-sonnet', 'local']:
            if name in self.providers:
                return self.providers[name]
        
        raise ValueError("No LLM provider available")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        provider: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """
        Generate text using LLM
        """
        messages = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        messages.append(Message(role="user", content=prompt))
        
        llm = self.get_provider(provider)
        return await llm.generate(messages, temperature, max_tokens, **kwargs)
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        provider: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """
        Multi-turn chat
        """
        msg_objects = [Message(role=m["role"], content=m["content"]) for m in messages]
        llm = self.get_provider(provider)
        return await llm.generate(msg_objects, temperature, max_tokens, **kwargs)
    
    async def stream(
        self,
        prompt: str,
        system_prompt: str = None,
        provider: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream text generation
        """
        messages = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        messages.append(Message(role="user", content=prompt))
        
        llm = self.get_provider(provider)
        async for chunk in llm.generate_stream(messages, temperature, max_tokens, **kwargs):
            yield chunk
    
    async def explain_concept(
        self,
        concept: str,
        student_level: str = "intermediate",
        style: str = "balanced"
    ) -> LLMResponse:
        """
        Generate educational concept explanation
        """
        system_prompt = f"""You are an expert AI tutor. Explain concepts clearly and engagingly.

Student Level: {student_level}
Teaching Style: {style}

Guidelines:
- Use clear, accessible language
- Provide relevant examples
- Include code snippets when appropriate
- Highlight key points
- Address common misconceptions"""
        
        prompt = f"Explain the concept: {concept}"
        
        return await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7
        )
    
    async def validate_answer(
        self,
        question: str,
        student_answer: str,
        expected_answer: str
    ) -> Dict[str, Any]:
        """
        Validate student answer using LLM
        """
        system_prompt = """You are an expert educational assessor. Evaluate student answers fairly and provide constructive feedback.

Return a JSON response with:
- is_correct: boolean
- score: 0-100
- feedback: constructive feedback
- misconceptions: list of identified misconceptions
- hints: helpful hints for improvement"""
        
        prompt = f"""Question: {question}

Expected Answer: {expected_answer}

Student's Answer: {student_answer}

Evaluate the student's answer and provide detailed feedback."""
        
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3
        )
        
        try:
            # Parse JSON from response
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback
        return {
            'is_correct': 'correct' in response.content.lower(),
            'score': 70,
            'feedback': response.content,
            'misconceptions': [],
            'hints': []
        }


# Global service instance
llm_service = LLMService()
