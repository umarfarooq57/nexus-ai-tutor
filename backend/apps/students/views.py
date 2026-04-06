"""
Students App Views
API endpoints for student profiles, progress, analytics, and sessions
"""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import StudentProfile, LearningSession, DigitalTwin
from .serializers import (
    StudentProfileSerializer, 
    LearningSessionSerializer,
    StudentProgressSerializer,
    WeaknessAnalysisSerializer
)


class StudentProfileView(generics.RetrieveUpdateAPIView):
    """Get or update student profile"""
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = StudentProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile


class StudentProgressView(APIView):
    """Get comprehensive student progress data"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            profile = request.user.student_profile
        except StudentProfile.DoesNotExist:
            return Response(
                {'error': 'Student profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate overall progress
        progress_data = {
            'overall_progress': self._calculate_overall_progress(profile),
            'topics_completed': profile.topics_completed,
            'total_study_time': profile.total_study_time,
            'current_streak': profile.streak_days,
            'mastery_breakdown': profile.mastery_scores,
            'recent_activity': self._get_recent_activity(profile),
            'goals': profile.goals
        }
        
        return Response(progress_data)
    
    def _calculate_overall_progress(self, profile):
        scores = profile.mastery_scores or {}
        if not scores:
            return 0.0
        return sum(scores.values()) / len(scores)
    
    def _get_recent_activity(self, profile):
        sessions = LearningSession.objects.filter(
            student=profile
        ).order_by('-started_at')[:10]
        return LearningSessionSerializer(sessions, many=True).data


class LearningAnalyticsView(APIView):
    """Get detailed learning analytics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            profile = request.user.student_profile
            digital_twin = profile.digital_twin
        except (StudentProfile.DoesNotExist, DigitalTwin.DoesNotExist):
            return Response(
                {'error': 'Profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        analytics = {
            'cognitive_state': {
                'knowledge_embedding': digital_twin.knowledge_embedding[:10] if digital_twin.knowledge_embedding else [],
                'attention_patterns': digital_twin.attention_dynamics,
                'emotional_state': digital_twin.emotional_state,
                'cognitive_load': digital_twin.cognitive_load
            },
            'predictions': {
                'next_topics': digital_twin.predicted_next_topics,
                'performance_prediction': digital_twin.performance_prediction,
                'forgetting_prediction': digital_twin.forgetting_prediction
            },
            'learning_style': profile.learning_styles,
            'cognitive_profile': profile.cognitive_profile,
            'error_patterns': list(profile.error_patterns.values_list('error_type', flat=True).distinct()[:5])
        }
        
        return Response(analytics)


class WeaknessAnalysisView(APIView):
    """Analyze student weaknesses and suggest focus areas"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            profile = request.user.student_profile
        except StudentProfile.DoesNotExist:
            return Response(
                {'error': 'Profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get error patterns
        error_patterns = profile.error_patterns.all()
        
        # Analyze weaknesses
        weakness_analysis = {
            'weak_topics': self._identify_weak_topics(profile),
            'error_patterns': [
                {
                    'type': ep.error_type,
                    'frequency': ep.frequency,
                    'context': ep.context,
                    'topic': str(ep.topic_id) if ep.topic else None
                }
                for ep in error_patterns.order_by('-frequency')[:10]
            ],
            'recommended_actions': self._generate_recommendations(profile),
            'focus_priority': self._calculate_priority(profile)
        }
        
        return Response(weakness_analysis)
    
    def _identify_weak_topics(self, profile):
        scores = profile.mastery_scores or {}
        weak = [(topic, score) for topic, score in scores.items() if score < 0.5]
        return sorted(weak, key=lambda x: x[1])[:5]
    
    def _generate_recommendations(self, profile):
        recommendations = []
        weak_topics = self._identify_weak_topics(profile)
        
        for topic, score in weak_topics:
            if score < 0.3:
                recommendations.append({
                    'topic': topic,
                    'action': 'review_fundamentals',
                    'priority': 'high'
                })
            elif score < 0.5:
                recommendations.append({
                    'topic': topic,
                    'action': 'practice_exercises',
                    'priority': 'medium'
                })
        
        return recommendations
    
    def _calculate_priority(self, profile):
        # Prioritize topics based on weakness and importance
        return ['topic_1', 'topic_2', 'topic_3']  # Placeholder


class LearningSessionListView(generics.ListCreateAPIView):
    """List or create learning sessions"""
    serializer_class = LearningSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LearningSession.objects.filter(
            student__user=self.request.user
        ).order_by('-started_at')
    
    def perform_create(self, serializer):
        profile = self.request.user.student_profile
        serializer.save(student=profile)


class LearningSessionDetailView(generics.RetrieveUpdateAPIView):
    """Get or update a specific learning session"""
    serializer_class = LearningSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LearningSession.objects.filter(
            student__user=self.request.user
        )
