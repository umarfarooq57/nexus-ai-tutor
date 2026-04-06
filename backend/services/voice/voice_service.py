"""
NEXUS AI Tutor - Voice Interaction Service
Speech-to-Text and Text-to-Speech for voice-based learning
"""

import asyncio
from typing import Dict, Optional, Any, AsyncGenerator, BinaryIO
from dataclasses import dataclass
import logging
import base64
import io
import os

logger = logging.getLogger('nexus.voice')


@dataclass
class TranscriptionResult:
    """Result of speech-to-text"""
    text: str
    language: str
    confidence: float
    duration: float
    segments: list


@dataclass
class SpeechResult:
    """Result of text-to-speech"""
    audio_data: bytes
    format: str
    duration: float
    voice_used: str


class VoiceService:
    """
    Voice Interaction Service
    Provides speech-to-text and text-to-speech capabilities
    """
    
    SUPPORTED_LANGUAGES = ['en', 'ur', 'hi', 'ar', 'es', 'fr', 'de', 'zh']
    VOICE_PRESETS = {
        'default': {'voice': 'alloy', 'speed': 1.0},
        'professor': {'voice': 'onyx', 'speed': 0.9},
        'friendly': {'voice': 'nova', 'speed': 1.1},
        'calm': {'voice': 'shimmer', 'speed': 0.95}
    }
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.whisper_model = None
        self.tts_cache = {}
    
    async def transcribe_audio(
        self,
        audio_file: BinaryIO,
        language: str = 'en',
        use_local: bool = False
    ) -> TranscriptionResult:
        """
        Transcribe audio to text using Whisper
        
        Args:
            audio_file: Audio file (WAV, MP3, etc.)
            language: Target language code
            use_local: Use local Whisper model instead of API
        """
        if use_local:
            return await self._transcribe_local(audio_file, language)
        else:
            return await self._transcribe_api(audio_file, language)
    
    async def _transcribe_api(
        self, 
        audio_file: BinaryIO, 
        language: str
    ) -> TranscriptionResult:
        """Transcribe using OpenAI Whisper API"""
        import httpx
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        audio_data = audio_file.read()
        
        async with httpx.AsyncClient() as client:
            files = {
                'file': ('audio.wav', audio_data, 'audio/wav'),
            }
            data = {
                'model': 'whisper-1',
                'language': language,
                'response_format': 'verbose_json'
            }
            
            response = await client.post(
                'https://api.openai.com/v1/audio/transcriptions',
                headers={'Authorization': f'Bearer {self.openai_api_key}'},
                files=files,
                data=data,
                timeout=60.0
            )
            
            result = response.json()
            
            return TranscriptionResult(
                text=result.get('text', ''),
                language=result.get('language', language),
                confidence=0.95,  # Whisper doesn't return confidence
                duration=result.get('duration', 0),
                segments=result.get('segments', [])
            )
    
    async def _transcribe_local(
        self, 
        audio_file: BinaryIO, 
        language: str
    ) -> TranscriptionResult:
        """Transcribe using local Whisper model"""
        try:
            import whisper
            
            if self.whisper_model is None:
                self.whisper_model = whisper.load_model("base")
            
            # Save to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                f.write(audio_file.read())
                temp_path = f.name
            
            try:
                result = self.whisper_model.transcribe(
                    temp_path,
                    language=language
                )
                
                return TranscriptionResult(
                    text=result['text'],
                    language=result.get('language', language),
                    confidence=0.9,
                    duration=0,
                    segments=result.get('segments', [])
                )
            finally:
                os.unlink(temp_path)
                
        except ImportError:
            logger.error("Whisper not installed, falling back to API")
            return await self._transcribe_api(audio_file, language)
    
    async def text_to_speech(
        self,
        text: str,
        voice_preset: str = 'default',
        output_format: str = 'mp3'
    ) -> SpeechResult:
        """
        Convert text to speech
        
        Args:
            text: Text to convert
            voice_preset: Voice preset name
            output_format: Output format (mp3, wav, opus)
        """
        # Check cache
        cache_key = f"{text[:50]}_{voice_preset}"
        if cache_key in self.tts_cache:
            return self.tts_cache[cache_key]
        
        preset = self.VOICE_PRESETS.get(voice_preset, self.VOICE_PRESETS['default'])
        
        result = await self._tts_api(text, preset, output_format)
        
        # Cache result
        if len(self.tts_cache) < 100:
            self.tts_cache[cache_key] = result
        
        return result
    
    async def _tts_api(
        self, 
        text: str, 
        preset: Dict, 
        output_format: str
    ) -> SpeechResult:
        """Generate speech using OpenAI TTS API"""
        import httpx
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                'https://api.openai.com/v1/audio/speech',
                headers={
                    'Authorization': f'Bearer {self.openai_api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'tts-1',
                    'input': text,
                    'voice': preset['voice'],
                    'speed': preset['speed'],
                    'response_format': output_format
                },
                timeout=60.0
            )
            
            audio_data = response.content
            
            return SpeechResult(
                audio_data=audio_data,
                format=output_format,
                duration=len(text) / 15,  # Rough estimate
                voice_used=preset['voice']
            )
    
    async def stream_tts(
        self,
        text: str,
        voice_preset: str = 'default'
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream text-to-speech for long content
        """
        # Split text into chunks for streaming
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            result = await self.text_to_speech(sentence + '.', voice_preset)
            yield result.audio_data
    
    async def voice_conversation(
        self,
        audio_input: BinaryIO,
        conversation_history: list,
        system_prompt: str = None
    ) -> Dict[str, Any]:
        """
        Complete voice conversation: transcribe -> LLM -> speak
        
        Returns both text and audio response
        """
        # 1. Transcribe user's speech
        transcription = await self.transcribe_audio(audio_input)
        
        # 2. Get LLM response
        from services.llm import llm_service
        
        messages = conversation_history + [
            {'role': 'user', 'content': transcription.text}
        ]
        
        if system_prompt:
            messages = [{'role': 'system', 'content': system_prompt}] + messages
        
        llm_response = await llm_service.chat(messages)
        
        # 3. Convert response to speech
        speech = await self.text_to_speech(
            llm_response.content,
            voice_preset='professor'
        )
        
        return {
            'user_text': transcription.text,
            'assistant_text': llm_response.content,
            'audio_response': base64.b64encode(speech.audio_data).decode(),
            'audio_format': speech.format
        }


# Global instance
voice_service = VoiceService()
