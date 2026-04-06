"""
NEXUS AI Tutor - Course & Content Models
Comprehensive course structure with multi-modal content support
"""

import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from datetime import timedelta


class Course(models.Model):
    """Course structure - top level container"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic Info
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500)
    
    # Category
    CATEGORY_CHOICES = [
        ('ai_ml', 'AI/Machine Learning'),
        ('data_science', 'Data Science'),
        ('fullstack', 'Full-Stack Development'),
        ('devops', 'DevOps & Cloud'),
        ('hybrid', 'Hybrid Programming'),
        ('fundamentals', 'Programming Fundamentals'),
    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    subcategory = models.CharField(max_length=100, blank=True, null=True)
    tags = ArrayField(models.CharField(max_length=50), default=list)
    
    # Difficulty
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    difficulty_score = models.FloatField(default=0.5)  # 0-1 for ML models
    
    # Media
    thumbnail = models.URLField(blank=True, null=True)
    preview_video = models.URLField(blank=True, null=True)
    
    # Prerequisites
    prerequisites = models.ManyToManyField(
        'self', 
        blank=True, 
        symmetrical=False,
        related_name='required_for'
    )
    required_skills = models.JSONField(default=list)
    
    # Metadata
    estimated_duration = models.DurationField(default=timedelta(hours=10))
    total_modules = models.IntegerField(default=0)
    total_topics = models.IntegerField(default=0)
    
    # Status
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Stats
    enrollment_count = models.IntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    average_rating = models.FloatField(default=0.0)
    
    # Embedding for semantic search
    embedding = ArrayField(
        models.FloatField(),
        size=768,
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'courses'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title


class Module(models.Model):
    """Course module - grouping of related topics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules'
    )
    
    # Basic Info
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.IntegerField()
    
    # Learning Objectives
    learning_objectives = models.JSONField(default=list)
    skills_gained = models.JSONField(default=list)
    
    # Metadata
    estimated_duration = models.DurationField(default=timedelta(hours=2))
    total_topics = models.IntegerField(default=0)
    
    # Status
    is_published = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'modules'
        ordering = ['course', 'order']
        unique_together = ['course', 'order']
        
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Topic(models.Model):
    """Individual topic within a module"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='topics'
    )
    
    # Basic Info
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.IntegerField()
    
    # Content Type
    CONTENT_TYPE_CHOICES = [
        ('theory', 'Theory/Concept'),
        ('practical', 'Practical/Hands-on'),
        ('project', 'Project'),
        ('review', 'Review'),
        ('assessment', 'Assessment'),
    ]
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    
    # Difficulty (can differ from course difficulty)
    difficulty_score = models.FloatField(default=0.5)
    
    # Prerequisites within the course
    prerequisite_topics = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='dependent_topics'
    )
    
    # Metadata
    estimated_duration = models.DurationField(default=timedelta(minutes=30))
    
    # Knowledge Graph Node Info
    concept_keywords = ArrayField(models.CharField(max_length=100), default=list)
    related_concepts = models.JSONField(default=list)
    
    # Embedding
    embedding = ArrayField(
        models.FloatField(),
        size=768,
        null=True,
        blank=True
    )
    
    # Status
    is_published = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'topics'
        ordering = ['module', 'order']
        unique_together = ['module', 'order']
        
    def __str__(self):
        return f"{self.module.course.title} - {self.title}"


class Content(models.Model):
    """Multi-modal content associated with topics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='contents'
    )
    
    # Content Type
    CONTENT_TYPE_CHOICES = [
        ('text', 'Rich Text'),
        ('markdown', 'Markdown'),
        ('code', 'Code Block'),
        ('image', 'Image'),
        ('diagram', 'Diagram'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('pdf', 'PDF Document'),
        ('docx', 'Word Document'),
        ('interactive', 'Interactive Widget'),
        ('quiz', 'Embedded Quiz'),
        ('project', 'Project Template'),
    ]
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    
    # Basic Info
    title = models.CharField(max_length=255)
    order = models.IntegerField()
    
    # Content Data
    content_data = models.JSONField(default=dict)  # Structured content
    raw_content = models.TextField(blank=True)  # For text/markdown/code
    file_url = models.URLField(null=True, blank=True)  # For media files
    
    # For Code
    programming_language = models.CharField(max_length=50, blank=True, null=True)
    is_executable = models.BooleanField(default=False)
    
    # For Images/Diagrams
    alt_text = models.TextField(blank=True)
    diagram_type = models.CharField(max_length=50, blank=True, null=True)
    labeled_components = models.JSONField(default=list)  # Detected components
    
    # For Video/Audio
    duration_seconds = models.IntegerField(null=True, blank=True)
    transcript = models.TextField(blank=True)
    keyframes = models.JSONField(default=list)  # Extracted keyframes
    
    # Processing Status
    is_processed = models.BooleanField(default=False)
    processing_metadata = models.JSONField(default=dict)
    
    # Difficulty (can vary from topic)
    difficulty_score = models.FloatField(default=0.5)
    
    # Presentation Style
    STYLE_CHOICES = [
        ('detailed', 'Detailed Explanation'),
        ('concise', 'Concise Summary'),
        ('example_heavy', 'Example Heavy'),
        ('visual', 'Visual Focus'),
        ('interactive', 'Interactive'),
    ]
    presentation_style = models.CharField(
        max_length=20,
        choices=STYLE_CHOICES,
        default='detailed'
    )
    
    # Embedding
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
        db_table = 'contents'
        ordering = ['topic', 'order']
        
    def __str__(self):
        return f"{self.topic.title} - {self.title}"


class ContentVersion(models.Model):
    """Version control for content (for A/B testing and rollback)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.ForeignKey(
        Content,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    
    version_number = models.IntegerField()
    content_data = models.JSONField()
    raw_content = models.TextField(blank=True)
    
    # A/B Testing
    is_active = models.BooleanField(default=False)
    traffic_percentage = models.FloatField(default=0.0)
    
    # Performance Metrics
    views = models.IntegerField(default=0)
    avg_time_spent = models.DurationField(null=True, blank=True)
    engagement_score = models.FloatField(null=True, blank=True)
    
    # Metadata
    change_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True
    )
    
    class Meta:
        db_table = 'content_versions'
        unique_together = ['content', 'version_number']
        ordering = ['-version_number']


class Enrollment(models.Model):
    """Student course enrollment"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    # Progress
    progress_percentage = models.FloatField(default=0.0)
    completed_topics = models.ManyToManyField(Topic, blank=True)
    current_topic = models.ForeignKey(
        Topic,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_learners'
    )
    
    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Time Tracking
    time_spent = models.DurationField(default=timedelta(0))
    
    # Completion
    completed_at = models.DateTimeField(null=True, blank=True)
    certificate_issued = models.BooleanField(default=False)
    
    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'enrollments'
        unique_together = ['student', 'course']
        
    def __str__(self):
        return f"{self.student.user.email} - {self.course.title}"
