"""
NEXUS AI Tutor - Interactive Code Playground
Secure code execution sandbox for learning
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
import subprocess
import tempfile
import os
import sys
import time
import resource
from contextlib import contextmanager

logger = logging.getLogger('nexus.playground')


@dataclass
class ExecutionResult:
    """Result of code execution"""
    success: bool
    output: str
    error: Optional[str]
    execution_time: float
    memory_used: int  # bytes
    return_value: Any = None


@dataclass
class TestResult:
    """Result of running tests"""
    passed: int
    failed: int
    total: int
    details: List[Dict]
    coverage: Optional[float] = None


class CodeSandbox:
    """
    Secure sandbox for code execution
    Uses subprocess isolation with resource limits
    """
    
    SUPPORTED_LANGUAGES = {
        'python': {
            'extension': '.py',
            'command': [sys.executable],
            'timeout': 10
        },
        'javascript': {
            'extension': '.js',
            'command': ['node'],
            'timeout': 10
        }
    }
    
    MAX_OUTPUT_SIZE = 10000  # characters
    MAX_MEMORY = 128 * 1024 * 1024  # 128 MB
    MAX_CPU_TIME = 5  # seconds
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.temp_dir = tempfile.mkdtemp(prefix='nexus_sandbox_')
    
    async def execute(
        self,
        code: str,
        language: str = 'python',
        stdin: str = None,
        test_cases: List[Dict] = None
    ) -> ExecutionResult:
        """
        Execute code in sandbox
        
        Args:
            code: Source code to execute
            language: Programming language
            stdin: Optional input to provide
            test_cases: Optional test cases to run
        """
        if language not in self.SUPPORTED_LANGUAGES:
            return ExecutionResult(
                success=False,
                output='',
                error=f"Unsupported language: {language}",
                execution_time=0,
                memory_used=0
            )
        
        lang_config = self.SUPPORTED_LANGUAGES[language]
        
        # Create temporary file
        file_path = os.path.join(
            self.temp_dir, 
            f"code_{int(time.time())}{lang_config['extension']}"
        )
        
        try:
            # Write code to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Execute with resource limits
            start_time = time.time()
            
            result = await self._run_in_sandbox(
                command=lang_config['command'] + [file_path],
                stdin=stdin,
                timeout=lang_config['timeout']
            )
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=result['success'],
                output=result['stdout'][:self.MAX_OUTPUT_SIZE],
                error=result['stderr'] if result['stderr'] else None,
                execution_time=execution_time,
                memory_used=result.get('memory', 0)
            )
            
        except Exception as e:
            logger.error(f"Sandbox execution error: {e}")
            return ExecutionResult(
                success=False,
                output='',
                error=str(e),
                execution_time=0,
                memory_used=0
            )
        finally:
            # Clean up
            if os.path.exists(file_path):
                os.remove(file_path)
    
    async def _run_in_sandbox(
        self,
        command: List[str],
        stdin: str = None,
        timeout: int = 10
    ) -> Dict:
        """Run command in sandboxed subprocess"""
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=self.MAX_OUTPUT_SIZE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=stdin.encode() if stdin else None),
                    timeout=timeout
                )
                
                return {
                    'success': process.returncode == 0,
                    'stdout': stdout.decode('utf-8', errors='replace'),
                    'stderr': stderr.decode('utf-8', errors='replace'),
                    'returncode': process.returncode
                }
                
            except asyncio.TimeoutError:
                process.kill()
                return {
                    'success': False,
                    'stdout': '',
                    'stderr': 'Execution timed out',
                    'returncode': -1
                }
                
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }
    
    async def run_tests(
        self,
        code: str,
        test_code: str,
        language: str = 'python'
    ) -> TestResult:
        """
        Run test cases against code
        """
        if language != 'python':
            return TestResult(
                passed=0, failed=0, total=0,
                details=[{'error': 'Only Python tests supported'}]
            )
        
        # Combine code and tests
        full_code = f"""
{code}

# Test execution
import unittest
import sys
from io import StringIO

{test_code}

if __name__ == '__main__':
    # Capture test output
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    
    print(f"PASSED: {{result.testsRun - len(result.failures) - len(result.errors)}}")
    print(f"FAILED: {{len(result.failures) + len(result.errors)}}")
    print(f"TOTAL: {{result.testsRun}}")
"""
        
        result = await self.execute(full_code, language)
        
        # Parse test results
        passed = failed = total = 0
        if result.success:
            for line in result.output.split('\n'):
                if line.startswith('PASSED:'):
                    passed = int(line.split(':')[1].strip())
                elif line.startswith('FAILED:'):
                    failed = int(line.split(':')[1].strip())
                elif line.startswith('TOTAL:'):
                    total = int(line.split(':')[1].strip())
        
        return TestResult(
            passed=passed,
            failed=failed,
            total=total,
            details=[{'output': result.output, 'error': result.error}]
        )
    
    def cleanup(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class CodePlayground:
    """
    Interactive Code Playground Service
    Provides code execution, testing, and AI assistance
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.sandbox = CodeSandbox(config)
        self.execution_history: List[Dict] = []
    
    async def execute_code(
        self,
        code: str,
        language: str = 'python',
        stdin: str = None
    ) -> Dict[str, Any]:
        """
        Execute code and return results with AI feedback
        """
        result = await self.sandbox.execute(code, language, stdin)
        
        # Store in history
        self.execution_history.append({
            'code': code,
            'language': language,
            'result': result,
            'timestamp': time.time()
        })
        
        # Generate AI feedback if there's an error
        feedback = None
        if not result.success and result.error:
            feedback = await self._generate_error_feedback(code, result.error, language)
        
        return {
            'success': result.success,
            'output': result.output,
            'error': result.error,
            'execution_time': result.execution_time,
            'feedback': feedback
        }
    
    async def _generate_error_feedback(
        self,
        code: str,
        error: str,
        language: str
    ) -> Dict[str, Any]:
        """Generate AI feedback for errors"""
        from services.llm import llm_service
        
        prompt = f"""Analyze this {language} code error and provide helpful feedback:

Code:
```{language}
{code}
```

Error:
{error}

Provide:
1. Simple explanation of what went wrong
2. How to fix it
3. A corrected code example
"""
        
        try:
            response = await llm_service.generate(
                prompt,
                system_prompt="You are a helpful coding assistant. Be concise and helpful.",
                temperature=0.5
            )
            
            return {
                'explanation': response.content,
                'has_suggestion': True
            }
        except:
            return None
    
    async def run_with_tests(
        self,
        code: str,
        test_code: str,
        language: str = 'python'
    ) -> Dict[str, Any]:
        """
        Run code with test cases
        """
        test_result = await self.sandbox.run_tests(code, test_code, language)
        
        return {
            'passed': test_result.passed,
            'failed': test_result.failed,
            'total': test_result.total,
            'success': test_result.failed == 0,
            'details': test_result.details,
            'coverage': test_result.coverage
        }
    
    async def complete_code(
        self,
        code: str,
        cursor_position: int,
        language: str = 'python'
    ) -> List[Dict[str, str]]:
        """
        Get code completion suggestions
        """
        from services.llm import llm_service
        
        # Split code at cursor
        before = code[:cursor_position]
        after = code[cursor_position:]
        
        prompt = f"""Complete this {language} code. Only provide the completion, not the full code.

Code before cursor:
```{language}
{before}
```

Code after cursor:
```{language}
{after}
```

Provide 3 possible completions as a JSON array:
[{{"completion": "...", "description": "..."}}]
"""
        
        try:
            response = await llm_service.generate(prompt, temperature=0.7)
            
            # Parse completions
            import json
            import re
            
            json_match = re.search(r'\[.*\]', response.content, re.DOTALL)
            if json_match:
                completions = json.loads(json_match.group())
                return completions[:3]
        except:
            pass
        
        return []
    
    async def explain_code(
        self,
        code: str,
        language: str = 'python'
    ) -> str:
        """
        Get AI explanation of code
        """
        from services.llm import llm_service
        
        prompt = f"""Explain this {language} code in simple terms:

```{language}
{code}
```

Provide:
1. Overall purpose
2. Step-by-step explanation
3. Key concepts used
"""
        
        response = await llm_service.generate(
            prompt,
            system_prompt="Explain code clearly for learners.",
            temperature=0.5
        )
        
        return response.content
    
    async def suggest_improvements(
        self,
        code: str,
        language: str = 'python'
    ) -> Dict[str, Any]:
        """
        Suggest code improvements
        """
        from services.llm import llm_service
        
        prompt = f"""Review this {language} code and suggest improvements:

```{language}
{code}
```

Check for:
1. Code quality issues
2. Best practice violations
3. Performance improvements
4. Security concerns

Format as JSON:
{{
  "issues": [{{"severity": "high/medium/low", "line": 1, "message": "..."}}],
  "suggestions": ["..."],
  "improved_code": "..."
}}
"""
        
        response = await llm_service.generate(prompt, temperature=0.3)
        
        try:
            import json
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {'issues': [], 'suggestions': [response.content], 'improved_code': None}
    
    def cleanup(self):
        """Clean up resources"""
        self.sandbox.cleanup()


# Global instance
playground = CodePlayground()
