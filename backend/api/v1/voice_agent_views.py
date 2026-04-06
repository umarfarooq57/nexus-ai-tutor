"""
NEXUS AI Tutor - Voice & Agent API Views
REST endpoints for voice interaction and agentic AI
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser
from django.http import StreamingHttpResponse
import asyncio
import base64


class VoiceTranscribeView(APIView):
    """Transcribe audio to text"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    
    def post(self, request):
        audio_file = request.FILES.get('audio')
        language = request.data.get('language', 'en')
        use_local = request.data.get('use_local', False)
        
        if not audio_file:
            return Response(
                {'error': 'No audio file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from services.voice import voice_service
            
            result = asyncio.run(voice_service.transcribe_audio(
                audio_file,
                language=language,
                use_local=use_local
            ))
            
            return Response({
                'text': result.text,
                'language': result.language,
                'confidence': result.confidence,
                'duration': result.duration
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VoiceSpeakView(APIView):
    """Convert text to speech"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        text = request.data.get('text')
        voice_preset = request.data.get('voice', 'default')
        output_format = request.data.get('format', 'mp3')
        
        if not text:
            return Response(
                {'error': 'No text provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from services.voice import voice_service
            
            result = asyncio.run(voice_service.text_to_speech(
                text,
                voice_preset=voice_preset,
                output_format=output_format
            ))
            
            return Response({
                'audio': base64.b64encode(result.audio_data).decode(),
                'format': result.format,
                'duration': result.duration,
                'voice': result.voice_used
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VoiceConversationView(APIView):
    """Voice-to-voice conversation with AI"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    
    def post(self, request):
        audio_file = request.FILES.get('audio')
        history = request.data.get('history', [])
        
        if not audio_file:
            return Response(
                {'error': 'No audio file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from services.voice import voice_service
            
            # Parse history if it's a string
            if isinstance(history, str):
                import json
                history = json.loads(history)
            
            result = asyncio.run(voice_service.voice_conversation(
                audio_file,
                conversation_history=history,
                system_prompt="You are a helpful AI tutor."
            ))
            
            return Response(result)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AgentChatView(APIView):
    """Chat with an AI agent"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        message = request.data.get('message')
        subject = request.data.get('subject', 'general')
        agent_id = request.data.get('agent_id')
        context = request.data.get('context', {})
        
        if not message:
            return Response(
                {'error': 'No message provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from services.agents import orchestrator, TeachingAgentFactory
            
            # Create or get agent
            if agent_id and agent_id in orchestrator.agents:
                agent = orchestrator.agents[agent_id]
            else:
                agent = TeachingAgentFactory.create(subject)
                orchestrator.register_agent(agent)
            
            # Run agent
            response = asyncio.run(agent.run(message, context))
            
            return Response({
                'response': response,
                'agent_id': agent.agent_id,
                'agent_name': agent.name,
                'thoughts': [
                    {'thought': t.thought, 'action': t.action.action_type if t.action else None}
                    for t in agent.thoughts[-3:]
                ]
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AgentListView(APIView):
    """List available agents"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from services.agents import orchestrator, TeachingAgentFactory
        
        agents = [
            {
                'id': agent.agent_id,
                'name': agent.name,
                'role': agent.role.value,
                'status': agent.status.value
            }
            for agent in orchestrator.agents.values()
        ]
        
        available_subjects = TeachingAgentFactory.list_available()
        
        return Response({
            'active_agents': agents,
            'available_subjects': available_subjects
        })


class MultiAgentSolveView(APIView):
    """Collaborative problem solving with multiple agents"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        task = request.data.get('task')
        roles = request.data.get('roles', ['tutor', 'reviewer'])
        
        if not task:
            return Response(
                {'error': 'No task provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from services.agents import orchestrator, AgentRole
            
            # Convert role strings to enum
            agent_roles = []
            for role in roles:
                try:
                    agent_roles.append(AgentRole(role))
                except:
                    pass
            
            if not agent_roles:
                agent_roles = [AgentRole.TUTOR]
            
            results = asyncio.run(orchestrator.collaborative_solve(task, agent_roles))
            
            return Response({
                'results': results,
                'roles_used': [r.value for r in agent_roles]
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CodeExecuteView(APIView):
    """Execute code in sandbox"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        code = request.data.get('code')
        language = request.data.get('language', 'python')
        stdin = request.data.get('stdin')
        
        if not code:
            return Response(
                {'error': 'No code provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from services.playground import playground
            
            result = asyncio.run(playground.execute_code(code, language, stdin))
            
            return Response(result)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CodeTestView(APIView):
    """Run tests on code"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        code = request.data.get('code')
        test_code = request.data.get('test_code')
        language = request.data.get('language', 'python')
        
        if not code or not test_code:
            return Response(
                {'error': 'Code and test_code are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from services.playground import playground
            
            result = asyncio.run(playground.run_with_tests(code, test_code, language))
            
            return Response(result)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CodeExplainView(APIView):
    """Get AI explanation of code"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        code = request.data.get('code')
        language = request.data.get('language', 'python')
        
        if not code:
            return Response(
                {'error': 'No code provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from services.playground import playground
            
            explanation = asyncio.run(playground.explain_code(code, language))
            
            return Response({'explanation': explanation})
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CodeImproveView(APIView):
    """Get code improvement suggestions"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        code = request.data.get('code')
        language = request.data.get('language', 'python')
        
        if not code:
            return Response(
                {'error': 'No code provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from services.playground import playground
            
            result = asyncio.run(playground.suggest_improvements(code, language))
            
            return Response(result)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
