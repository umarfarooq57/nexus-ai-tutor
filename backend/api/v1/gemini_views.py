"""
Gemini AI Chat Views
API endpoint for Gemini-powered AI assistant
"""

import os
import json
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings


class GeminiChatView(APIView):
    """Chat with Gemini AI"""
    permission_classes = [permissions.AllowAny]  # Allow without auth for testing
    
    def post(self, request):
        message = request.data.get('message', '')
        subject = request.data.get('subject', 'General')
        
        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.environ.get('GEMINI_API_KEY', '')
        
        if not api_key:
            return Response({'error': 'Gemini API key not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            # Gemini API endpoint
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            
            # System prompt for focused learning assistant
            system_prompt = f"""You are a helpful AI learning assistant specialized in {subject}. 
Keep your responses concise and focused. Only answer what is asked.
Do not add unnecessary explanations or go off-topic.
If asked about code, provide short, working examples.
Use markdown formatting for code blocks."""

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{system_prompt}\n\nUser: {message}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1024,
                }
            }
            
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract text from Gemini response
            if 'candidates' in data and len(data['candidates']) > 0:
                ai_response = data['candidates'][0]['content']['parts'][0]['text']
            else:
                ai_response = "I couldn't generate a response. Please try again."
            
            return Response({
                'response': ai_response,
                'success': True
            })
            
        except requests.exceptions.Timeout:
            return Response({'error': 'Request timed out', 'response': 'Sorry, the request took too long. Please try again.'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        except requests.exceptions.RequestException as e:
            return Response({'error': str(e), 'response': 'Failed to connect to AI service.'}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            return Response({'error': str(e), 'response': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
