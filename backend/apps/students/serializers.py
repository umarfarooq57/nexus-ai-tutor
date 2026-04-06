"""
Students App Serializers
"""

from rest_framework import serializers
from .models import StudentProfile, DigitalTwin, TopicMastery, LearningSession, ErrorPattern


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for student profile"""
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'username', 'email', 'learning_styles', 
            'cognitive_profile', 'mastery_scores', 'total_study_time',
            'topics_completed', 'streak_days', 'goals', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'topics_completed', 'streak_days']


class DigitalTwinSerializer(serializers.ModelSerializer):
    """Serializer for digital twin state"""
    
    class Meta:
        model = DigitalTwin
        fields = [
            'knowledge_graph_state', 'emotional_state', 'cognitive_load',
            'attention_dynamics', 'performance_prediction', 
            'predicted_next_topics', 'updated_at'
        ]
        read_only_fields = ['updated_at']


class TopicMasterySerializer(serializers.ModelSerializer):
    """Serializer for topic mastery"""
    topic_name = serializers.CharField(source='topic.title', read_only=True)
    
    class Meta:
        model = TopicMastery
        fields = [
            'id', 'topic', 'topic_name', 'mastery_level', 
            'confidence_level', 'practice_count', 'retention_strength',
            'last_practiced', 'next_review'
        ]


class LearningSessionSerializer(serializers.ModelSerializer):
    """Serializer for learning sessions"""
    
    class Meta:
        model = LearningSession
        fields = [
            'id', 'content', 'started_at', 'ended_at', 'duration_seconds',
            'engagement_score', 'focus_score', 'comprehension_score',
            'emotional_journey', 'ai_actions', 'completed'
        ]
        read_only_fields = ['id', 'started_at', 'duration_seconds']


class ErrorPatternSerializer(serializers.ModelSerializer):
    """Serializer for error patterns"""
    
    class Meta:
        model = ErrorPattern
        fields = [
            'id', 'error_type', 'topic', 'frequency', 'context',
            'resolution_strategies', 'last_occurred'
        ]


class StudentProgressSerializer(serializers.Serializer):
    """Serializer for student progress data"""
    overall_progress = serializers.FloatField()
    topics_completed = serializers.IntegerField()
    total_study_time = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    mastery_breakdown = serializers.DictField()
    recent_activity = LearningSessionSerializer(many=True)
    goals = serializers.DictField()


class WeaknessAnalysisSerializer(serializers.Serializer):
    """Serializer for weakness analysis"""
    weak_topics = serializers.ListField()
    error_patterns = serializers.ListField()
    recommended_actions = serializers.ListField()
    focus_priority = serializers.ListField()
