"""
NEXUS AI Tutor - Assessment Models
Comprehensive quiz, test, and evaluation system
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from datetime import timedelta


class Quiz(models.Model):
    """Quiz/Assessment container"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Association
    topic = models.ForeignKey(
        'courses.Topic',
        on_delete=models.CASCADE,
        related_name='quizzes',
        null=True,
        blank=True
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='quizzes',
        null=True,
        blank=True
    )
    
    # Basic Info
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Type
    QUIZ_TYPE_CHOICES = [
        ('practice', 'Practice Quiz'),
        ('assessment', 'Assessment'),
        ('exam', 'Final Exam'),
        ('diagnostic', 'Diagnostic Test'),
        ('adaptive', 'Adaptive Quiz'),
    ]
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPE_CHOICES)
    
    # Configuration
    time_limit = models.DurationField(null=True, blank=True)
    passing_score = models.FloatField(default=0.7)
    max_attempts = models.IntegerField(default=3)
    shuffle_questions = models.BooleanField(default=True)
    show_answers_after = models.BooleanField(default=True)
    
    # Difficulty
    difficulty_score = models.FloatField(default=0.5)
    is_adaptive = models.BooleanField(default=False)
    
    # Metadata
    total_questions = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    
    # Stats
    attempts_count = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    
    # Status
    is_published = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'quizzes'
        verbose_name_plural = 'Quizzes'
        
    def __str__(self):
        return self.title


class Question(models.Model):
    """Quiz question"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    
    # Question Type
    QUESTION_TYPE_CHOICES = [
        ('mcq_single', 'Multiple Choice (Single)'),
        ('mcq_multi', 'Multiple Choice (Multiple)'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('long_answer', 'Long Answer/Essay'),
        ('code', 'Code Writing'),
        ('code_output', 'Code Output Prediction'),
        ('fill_blank', 'Fill in the Blank'),
        ('matching', 'Matching'),
        ('ordering', 'Ordering/Sequence'),
        ('diagram_label', 'Diagram Labeling'),
    ]
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    
    # Question Content
    question_text = models.TextField()
    question_html = models.TextField(blank=True)  # Rendered HTML
    question_media = models.URLField(null=True, blank=True)
    
    # For Code Questions
    code_template = models.TextField(blank=True)
    programming_language = models.CharField(max_length=50, blank=True, null=True)
    test_cases = models.JSONField(default=list)
    
    # For Diagram Questions
    diagram_url = models.URLField(null=True, blank=True)
    label_positions = models.JSONField(default=list)
    
    # Options (for MCQ, Matching, etc.)
    options = models.JSONField(default=list)
    
    # Answer
    correct_answer = models.JSONField()  # Can be string, list, or dict
    answer_explanation = models.TextField(blank=True)
    
    # Hints
    hints = models.JSONField(default=list)
    
    # Scoring
    points = models.IntegerField(default=1)
    partial_credit = models.BooleanField(default=False)
    
    # Difficulty
    difficulty_score = models.FloatField(default=0.5)
    
    # Stats
    attempts_count = models.IntegerField(default=0)
    correct_rate = models.FloatField(default=0.0)
    avg_time_seconds = models.IntegerField(default=0)
    
    # Ordering
    order = models.IntegerField(default=0)
    
    # Embedding for semantic matching
    embedding = ArrayField(
        models.FloatField(),
        size=768,
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['quiz', 'order']
        
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"


class QuizAttempt(models.Model):
    """Student quiz attempt"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    
    # Attempt Info
    attempt_number = models.IntegerField(default=1)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    time_taken = models.DurationField(null=True, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('timed_out', 'Timed Out'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    # Score
    score = models.FloatField(null=True, blank=True)
    points_earned = models.IntegerField(default=0)
    max_points = models.IntegerField(default=0)
    passed = models.BooleanField(null=True, blank=True)
    
    # Answers
    answers = models.JSONField(default=dict)  # question_id: answer
    
    # Metrics
    questions_answered = models.IntegerField(default=0)
    correct_count = models.IntegerField(default=0)
    incorrect_count = models.IntegerField(default=0)
    skipped_count = models.IntegerField(default=0)
    
    # Hints Used
    hints_used = models.JSONField(default=dict)
    
    # Emotional/Cognitive State During Quiz
    cognitive_metrics = models.JSONField(default=dict)
    
    # For Adaptive Quizzes
    difficulty_progression = models.JSONField(default=list)
    
    class Meta:
        db_table = 'quiz_attempts'
        ordering = ['-started_at']
        
    def __str__(self):
        return f"{self.student.user.email} - {self.quiz.title} - Attempt {self.attempt_number}"


class QuestionResponse(models.Model):
    """Individual question response within an attempt"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    
    # Answer
    student_answer = models.JSONField()
    
    # Validation (by AI Answer Validator)
    is_correct = models.BooleanField(null=True, blank=True)
    partial_score = models.FloatField(null=True, blank=True)  # For partial credit
    points_awarded = models.IntegerField(default=0)
    
    # AI Feedback
    ai_feedback = models.TextField(blank=True)
    error_type = models.CharField(max_length=50, blank=True, null=True)
    misconception_detected = models.TextField(blank=True, null=True)
    
    # Hints
    hints_viewed = models.IntegerField(default=0)
    
    # Timing
    time_spent = models.DurationField(null=True, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    # Cognitive State
    confidence_reported = models.FloatField(null=True, blank=True)  # Student self-report
    
    class Meta:
        db_table = 'question_responses'
        unique_together = ['attempt', 'question']
        
    def __str__(self):
        return f"{self.attempt} - {self.question}"


class AdaptiveQuizState(models.Model):
    """State for adaptive quizzes using Item Response Theory"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.OneToOneField(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='adaptive_state'
    )
    
    # IRT Parameters
    estimated_ability = models.FloatField(default=0.0)  # Theta
    ability_variance = models.FloatField(default=1.0)
    
    # Question Selection
    questions_pool = models.JSONField(default=list)  # Available questions
    asked_questions = models.JSONField(default=list)  # Already asked
    next_question = models.ForeignKey(
        Question,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    # Convergence
    is_converged = models.BooleanField(default=False)
    convergence_threshold = models.FloatField(default=0.1)
    
    # History
    ability_history = ArrayField(models.FloatField(), default=list)
    
    class Meta:
        db_table = 'adaptive_quiz_states'


class AssessmentReport(models.Model):
    """Generated assessment report"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    attempt = models.OneToOneField(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='report'
    )
    
    # Report Content
    summary = models.TextField()
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    recommendations = models.JSONField(default=list)
    
    # Detailed Analysis
    topic_breakdown = models.JSONField(default=dict)
    error_analysis = models.JSONField(default=dict)
    comparison_to_peers = models.JSONField(default=dict)
    
    # Generated Files
    pdf_url = models.URLField(null=True, blank=True)
    docx_url = models.URLField(null=True, blank=True)
    
    # Generation
    generated_at = models.DateTimeField(auto_now_add=True)
    generation_model = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        db_table = 'assessment_reports'
        
    def __str__(self):
        return f"Report: {self.attempt}"
