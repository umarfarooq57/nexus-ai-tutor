"""
NEXUS AI Tutor - Student Brain Model & Digital Twin
The most advanced student profiling system ever built
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils import timezone
from datetime import timedelta


class StudentProfile(models.Model):
    """Core student profile with cognitive fingerprint"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='student_profile'
    )
    
    # Learning Style Classification
    LEARNING_STYLE_CHOICES = [
        ('visual', 'Visual Learner'),
        ('auditory', 'Auditory Learner'),
        ('kinesthetic', 'Kinesthetic Learner'),
        ('reading', 'Reading/Writing Learner'),
        ('multimodal', 'Multimodal Learner'),
    ]
    primary_learning_style = models.CharField(
        max_length=20, 
        choices=LEARNING_STYLE_CHOICES,
        default='multimodal'
    )
    learning_style_scores = models.JSONField(default=dict)  # All style scores
    
    # Cognitive Profile
    preferred_difficulty = models.FloatField(default=0.5)  # 0-1 scale
    learning_speed = models.FloatField(default=1.0)  # Relative to average
    attention_span_minutes = models.IntegerField(default=25)  # Pomodoro-style
    optimal_session_duration = models.DurationField(default=timedelta(minutes=45))
    
    # Cognitive Style Vector (for ML models)
    cognitive_style_vector = ArrayField(
        models.FloatField(),
        size=256,
        null=True,
        blank=True
    )
    
    # Performance Metrics
    overall_mastery = models.FloatField(default=0.0)
    consistency_score = models.FloatField(default=0.0)
    engagement_score = models.FloatField(default=0.0)
    
    # Time Tracking
    total_study_time = models.DurationField(default=timedelta(0))
    total_sessions = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    
    # Goals
    daily_goal_minutes = models.IntegerField(default=60)
    weekly_goal_topics = models.IntegerField(default=5)
    
    # Emotional Baseline
    emotional_baseline = models.JSONField(default=dict)
    stress_tolerance = models.FloatField(default=0.5)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_profiles'
        
    def __str__(self):
        return f"Profile: {self.user.email}"


class DigitalTwin(models.Model):
    """Complete Digital Twin of Student's Cognitive State"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.OneToOneField(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='digital_twin'
    )
    
    # Knowledge Graph State (serialized graph representation)
    knowledge_graph_state = models.JSONField(default=dict)
    knowledge_graph_embedding = ArrayField(
        models.FloatField(),
        size=512,
        null=True,
        blank=True
    )
    
    # Memory Systems
    working_memory_snapshot = models.JSONField(default=dict)
    working_memory_capacity = models.IntegerField(default=7)  # Miller's Law
    long_term_memory_patterns = models.JSONField(default=dict)
    
    # Attention & Focus
    attention_dynamics = models.JSONField(default=dict)
    current_focus_topic = models.ForeignKey(
        'courses.Topic',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    attention_history = ArrayField(
        models.FloatField(),
        null=True,
        blank=True
    )
    
    # Emotional State
    current_emotional_state = models.JSONField(default=dict)
    emotional_history = models.JSONField(default=list)
    
    # Cognitive Load
    current_cognitive_load = models.FloatField(default=0.0)
    cognitive_load_threshold = models.FloatField(default=0.7)
    
    # Predictions
    predicted_performance = models.JSONField(default=dict)
    next_optimal_topics = models.JSONField(default=list)
    predicted_forgetting = models.JSONField(default=dict)
    
    # Sync
    last_sync = models.DateTimeField(auto_now=True)
    sync_version = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'digital_twins'
        
    def __str__(self):
        return f"Digital Twin: {self.student.user.email}"


class TopicMastery(models.Model):
    """Track mastery level for each topic"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='topic_masteries'
    )
    topic = models.ForeignKey(
        'courses.Topic',
        on_delete=models.CASCADE,
        related_name='student_masteries'
    )
    
    # Mastery Level
    mastery_level = models.FloatField(default=0.0)  # 0-1
    confidence_score = models.FloatField(default=0.0)  # Model confidence
    
    # Practice History
    attempts_count = models.IntegerField(default=0)
    correct_count = models.IntegerField(default=0)
    time_spent = models.DurationField(default=timedelta(0))
    
    # Memory Strength (for spaced repetition)
    retention_strength = models.FloatField(default=0.0)
    forgetting_curve_factor = models.FloatField(default=2.0)
    last_reviewed = models.DateTimeField(null=True, blank=True)
    next_review = models.DateTimeField(null=True, blank=True)
    review_count = models.IntegerField(default=0)
    
    # Activation
    activation_count = models.IntegerField(default=0)
    last_activated = models.DateTimeField(null=True, blank=True)
    activation_history = ArrayField(
        models.FloatField(),
        null=True,
        blank=True
    )
    
    # Misconceptions
    misconceptions = models.JSONField(default=list)
    
    # Timestamps
    first_encounter = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'topic_masteries'
        unique_together = ['student', 'topic']
        
    def __str__(self):
        return f"{self.student.user.email} - {self.topic.title}: {self.mastery_level:.2%}"
    
    def calculate_retention(self):
        """Calculate current retention based on forgetting curve"""
        if not self.last_reviewed:
            return 0.0
        
        days_since_review = (timezone.now() - self.last_reviewed).days
        retention = self.retention_strength * (self.forgetting_curve_factor ** (-days_since_review / 7))
        return max(0.0, min(1.0, retention))


class LearningSession(models.Model):
    """Track individual learning sessions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='learning_sessions'
    )
    
    # Session Details
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    
    # Content
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    topics_covered = models.ManyToManyField('courses.Topic', blank=True)
    content_consumed = models.JSONField(default=list)
    
    # Engagement Metrics
    focus_score = models.FloatField(null=True, blank=True)
    engagement_score = models.FloatField(null=True, blank=True)
    distraction_count = models.IntegerField(default=0)
    pause_count = models.IntegerField(default=0)
    
    # Emotional Tracking
    emotional_journey = models.JSONField(default=list)  # Time-series of emotions
    avg_cognitive_load = models.FloatField(null=True, blank=True)
    
    # Outcomes
    concepts_learned = models.IntegerField(default=0)
    quiz_attempts = models.IntegerField(default=0)
    average_quiz_score = models.FloatField(null=True, blank=True)
    
    # Agent Decisions
    teaching_actions = models.JSONField(default=list)  # Actions taken by AI
    rl_rewards = models.FloatField(null=True, blank=True)
    
    # Device Info
    device_type = models.CharField(max_length=50, blank=True, null=True)
    platform = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        db_table = 'learning_sessions'
        ordering = ['-started_at']
        
    def __str__(self):
        return f"Session: {self.student.user.email} - {self.started_at}"
    
    def end_session(self):
        """End the learning session and calculate metrics"""
        self.ended_at = timezone.now()
        self.duration = self.ended_at - self.started_at
        self.save()


class ErrorPattern(models.Model):
    """Track common error patterns for targeted improvement"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='error_patterns'
    )
    topic = models.ForeignKey(
        'courses.Topic',
        on_delete=models.CASCADE,
        related_name='error_patterns'
    )
    
    # Error Classification
    ERROR_TYPE_CHOICES = [
        ('conceptual', 'Conceptual Misunderstanding'),
        ('procedural', 'Procedural Error'),
        ('factual', 'Factual Error'),
        ('careless', 'Careless Mistake'),
        ('transferal', 'Transfer Error'),
        ('syntactic', 'Syntax Error'),
        ('semantic', 'Semantic Error'),
        ('logical', 'Logical Error'),
    ]
    error_type = models.CharField(max_length=50, choices=ERROR_TYPE_CHOICES)
    error_subtype = models.CharField(max_length=100, blank=True, null=True)
    
    # Details
    error_description = models.TextField()
    error_context = models.JSONField(default=dict)  # What the student was doing
    correct_solution = models.TextField(blank=True, null=True)
    
    # Frequency
    frequency = models.IntegerField(default=1)
    first_occurrence = models.DateTimeField(auto_now_add=True)
    last_occurrence = models.DateTimeField(auto_now=True)
    
    # Resolution
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_method = models.TextField(blank=True, null=True)
    
    # Embedding for similarity matching
    error_embedding = ArrayField(
        models.FloatField(),
        size=768,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'error_patterns'
        
    def __str__(self):
        return f"{self.student.user.email} - {self.error_type}: {self.error_description[:50]}"


class BehaviorMetrics(models.Model):
    """Daily behavior metrics aggregation"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name='behavior_metrics'
    )
    date = models.DateField()
    
    # Time Metrics
    total_active_time = models.DurationField(default=timedelta(0))
    total_sessions = models.IntegerField(default=0)
    avg_session_duration = models.DurationField(null=True, blank=True)
    
    # Engagement
    content_interaction_rate = models.FloatField(default=0.0)
    quiz_completion_rate = models.FloatField(default=0.0)
    hint_usage_rate = models.FloatField(default=0.0)
    
    # Focus
    avg_focus_score = models.FloatField(null=True, blank=True)
    distraction_rate = models.FloatField(default=0.0)
    pause_frequency = models.FloatField(default=0.0)
    
    # Progress
    topics_completed = models.IntegerField(default=0)
    quizzes_taken = models.IntegerField(default=0)
    avg_quiz_score = models.FloatField(null=True, blank=True)
    
    # Emotional
    dominant_emotion = models.CharField(max_length=50, blank=True, null=True)
    avg_cognitive_load = models.FloatField(null=True, blank=True)
    
    class Meta:
        db_table = 'behavior_metrics'
        unique_together = ['student', 'date']
        ordering = ['-date']
        
    def __str__(self):
        return f"{self.student.user.email} - {self.date}"


class CognitiveEvent(models.Model):
    """Track individual cognitive events for the Digital Twin"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    digital_twin = models.ForeignKey(
        DigitalTwin,
        on_delete=models.CASCADE,
        related_name='cognitive_events'
    )
    
    # Event Type
    EVENT_TYPE_CHOICES = [
        ('concept_learned', 'Concept Learned'),
        ('concept_reviewed', 'Concept Reviewed'),
        ('concept_forgotten', 'Concept Forgotten'),
        ('error_made', 'Error Made'),
        ('error_corrected', 'Error Corrected'),
        ('quiz_completed', 'Quiz Completed'),
        ('attention_shift', 'Attention Shift'),
        ('emotion_change', 'Emotion Change'),
        ('cognitive_overload', 'Cognitive Overload'),
        ('breakthrough', 'Learning Breakthrough'),
        ('struggle_detected', 'Struggle Detected'),
    ]
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    
    # Event Data
    event_data = models.JSONField(default=dict)
    related_topic = models.ForeignKey(
        'courses.Topic',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Metrics at Event Time
    cognitive_load = models.FloatField(null=True, blank=True)
    emotional_valence = models.FloatField(null=True, blank=True)  # -1 to 1
    attention_level = models.FloatField(null=True, blank=True)  # 0 to 1
    
    # Timestamp
    occurred_at = models.DateTimeField(auto_now_add=True)
    
    # Embedding for analysis
    event_embedding = ArrayField(
        models.FloatField(),
        size=768,
        null=True,
        blank=True
    )
    
    class Meta:
        db_table = 'cognitive_events'
        ordering = ['-occurred_at']
        
    def __str__(self):
        return f"{self.event_type} at {self.occurred_at}"


class PredictionLog(models.Model):
    """Log predictions made by the Digital Twin for validation"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    digital_twin = models.ForeignKey(
        DigitalTwin,
        on_delete=models.CASCADE,
        related_name='predictions'
    )
    
    # Prediction Details
    PREDICTION_TYPE_CHOICES = [
        ('quiz_score', 'Quiz Score Prediction'),
        ('retention', 'Retention Prediction'),
        ('next_topic', 'Next Topic Recommendation'),
        ('struggle', 'Struggle Prediction'),
        ('completion_time', 'Completion Time Prediction'),
        ('engagement', 'Engagement Prediction'),
    ]
    prediction_type = models.CharField(max_length=50, choices=PREDICTION_TYPE_CHOICES)
    
    # Values
    predicted_value = models.JSONField()
    actual_value = models.JSONField(null=True, blank=True)
    confidence = models.FloatField()
    
    # Accuracy (calculated after actual value is known)
    accuracy = models.FloatField(null=True, blank=True)
    error = models.FloatField(null=True, blank=True)
    
    # Context
    context = models.JSONField(default=dict)
    model_version = models.CharField(max_length=50, blank=True, null=True)
    
    # Timestamps
    predicted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'prediction_logs'
        ordering = ['-predicted_at']
        
    def __str__(self):
        return f"{self.prediction_type}: {self.predicted_value}"
    
    def verify(self, actual_value):
        """Verify prediction against actual value"""
        self.actual_value = actual_value
        self.verified_at = timezone.now()
        
        # Calculate accuracy based on prediction type
        if self.prediction_type in ['quiz_score', 'retention', 'engagement']:
            pred = self.predicted_value.get('value', 0)
            actual = actual_value.get('value', 0)
            self.error = abs(pred - actual)
            self.accuracy = max(0, 1 - self.error)
        
        self.save()
