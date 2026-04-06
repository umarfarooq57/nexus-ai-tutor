"""
Assessments App Serializers
"""

from rest_framework import serializers
from .models import Quiz, Question, QuizAttempt, QuestionResponse, AdaptiveQuizState


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for questions"""
    
    class Meta:
        model = Question
        fields = [
            'id', 'question_type', 'question_text', 'options',
            'hints', 'difficulty', 'points', 'order'
        ]
        # Never expose correct_answer in list views


class QuestionDetailSerializer(serializers.ModelSerializer):
    """Detailed question serializer with answer (for results)"""
    
    class Meta:
        model = Question
        fields = [
            'id', 'question_type', 'question_text', 'options',
            'correct_answer', 'explanation', 'difficulty', 'points'
        ]


class QuizSerializer(serializers.ModelSerializer):
    """Basic quiz serializer"""
    questions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'quiz_type', 'topic',
            'difficulty', 'questions_count', 'config', 'created_at'
        ]
    
    def get_questions_count(self, obj):
        return obj.questions.count()


class QuizDetailSerializer(serializers.ModelSerializer):
    """Detailed quiz serializer with questions"""
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'description', 'quiz_type', 'topic',
            'difficulty', 'config', 'questions', 'created_at'
        ]


class QuestionResponseSerializer(serializers.ModelSerializer):
    """Serializer for question responses"""
    question = QuestionDetailSerializer(read_only=True)
    
    class Meta:
        model = QuestionResponse
        fields = [
            'question', 'student_answer', 'is_correct',
            'time_taken_seconds', 'ai_feedback', 'hints_used'
        ]


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Serializer for quiz attempts"""
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'quiz_title', 'score', 'status',
            'started_at', 'ended_at', 'total_points'
        ]


class QuizResultSerializer(serializers.ModelSerializer):
    """Detailed quiz result serializer"""
    quiz = QuizSerializer(read_only=True)
    responses = QuestionResponseSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'quiz', 'score', 'status', 'started_at', 'ended_at',
            'total_points', 'responses', 'answers_summary'
        ]


class AdaptiveQuizStateSerializer(serializers.ModelSerializer):
    """Serializer for adaptive quiz state"""
    
    class Meta:
        model = AdaptiveQuizState
        fields = [
            'id', 'topic', 'estimated_ability', 'questions_answered',
            'question_pool', 'answered_question_ids'
        ]
