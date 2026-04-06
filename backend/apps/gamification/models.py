"""
NEXUS AI Tutor - Gamification System
XP, Levels, Achievements, Badges, and Streaks
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from datetime import timedelta
import uuid


class XPLevel(models.Model):
    """XP Level configuration"""
    level = models.IntegerField(unique=True)
    xp_required = models.IntegerField()
    title = models.CharField(max_length=100)
    badge_icon = models.CharField(max_length=50, default='⭐')
    perks = models.JSONField(default=list)  # List of perks unlocked
    
    class Meta:
        ordering = ['level']
    
    def __str__(self):
        return f"Level {self.level}: {self.title}"


class Achievement(models.Model):
    """Achievement definitions"""
    CATEGORY_CHOICES = [
        ('learning', 'Learning'),
        ('streak', 'Streak'),
        ('quiz', 'Quiz'),
        ('social', 'Social'),
        ('special', 'Special'),
    ]
    
    RARITY_CHOICES = [
        ('common', 'Common'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')
    icon = models.CharField(max_length=50)  # Emoji or icon name
    xp_reward = models.IntegerField(default=100)
    
    # Unlock conditions (JSON)
    conditions = models.JSONField(default=dict)
    # e.g., {"type": "streak", "value": 7} or {"type": "quiz_score", "value": 100}
    
    is_hidden = models.BooleanField(default=False)  # Secret achievements
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class Badge(models.Model):
    """Badge definitions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default='gold')
    category = models.CharField(max_length=50)
    tier = models.IntegerField(default=1)  # Bronze=1, Silver=2, Gold=3
    
    # Requirements
    requirements = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class StudentGamification(models.Model):
    """Student's gamification data"""
    student = models.OneToOneField(
        'students.StudentProfile',
        on_delete=models.CASCADE,
        related_name='gamification'
    )
    
    # XP & Level
    total_xp = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    current_level = models.IntegerField(default=1)
    xp_to_next_level = models.IntegerField(default=100)
    
    # Streaks
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    
    # Daily/Weekly stats
    daily_xp = models.IntegerField(default=0)
    weekly_xp = models.IntegerField(default=0)
    last_daily_reset = models.DateField(null=True, blank=True)
    last_weekly_reset = models.DateField(null=True, blank=True)
    
    # Achievements & Badges
    achievements = models.ManyToManyField(Achievement, through='StudentAchievement')
    badges = models.ManyToManyField(Badge, through='StudentBadge')
    
    # Stats
    total_quizzes_completed = models.IntegerField(default=0)
    total_lessons_completed = models.IntegerField(default=0)
    total_study_time_minutes = models.IntegerField(default=0)
    perfect_quiz_count = models.IntegerField(default=0)
    
    # Leaderboard opt-in
    show_on_leaderboard = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    def add_xp(self, amount: int, source: str = 'general'):
        """Add XP and check for level up"""
        self.total_xp += amount
        self.daily_xp += amount
        self.weekly_xp += amount
        
        # Check for level up
        while self.total_xp >= self.xp_to_next_level:
            self._level_up()
        
        self.save()
        return self.current_level
    
    def _level_up(self):
        """Handle level up"""
        self.current_level += 1
        # XP curve: each level requires more XP
        self.xp_to_next_level = int(100 * (1.5 ** (self.current_level - 1)))
    
    def update_streak(self):
        """Update streak based on activity"""
        today = timezone.now().date()
        
        if self.last_activity_date is None:
            self.current_streak = 1
        elif self.last_activity_date == today - timedelta(days=1):
            self.current_streak += 1
        elif self.last_activity_date < today - timedelta(days=1):
            self.current_streak = 1
        # If same day, streak stays the same
        
        self.last_activity_date = today
        
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        self.save()
        return self.current_streak
    
    def reset_daily(self):
        """Reset daily stats"""
        today = timezone.now().date()
        if self.last_daily_reset != today:
            self.daily_xp = 0
            self.last_daily_reset = today
            self.save()
    
    def reset_weekly(self):
        """Reset weekly stats"""
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        if self.last_weekly_reset != week_start:
            self.weekly_xp = 0
            self.last_weekly_reset = week_start
            self.save()


class StudentAchievement(models.Model):
    """Student's earned achievements"""
    student_gamification = models.ForeignKey(StudentGamification, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student_gamification', 'achievement']


class StudentBadge(models.Model):
    """Student's earned badges"""
    student_gamification = models.ForeignKey(StudentGamification, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(default=1.0)  # For progressive badges
    
    class Meta:
        unique_together = ['student_gamification', 'badge']


class DailyChallenge(models.Model):
    """Daily challenges for bonus XP"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=50)
    requirements = models.JSONField(default=dict)
    xp_reward = models.IntegerField(default=200)
    bonus_xp = models.IntegerField(default=50)  # For completing all daily challenges
    
    def __str__(self):
        return f"{self.date}: {self.title}"


class Leaderboard(models.Model):
    """Leaderboard snapshots"""
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('all_time', 'All Time'),
    ]
    
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    date = models.DateField()
    rankings = models.JSONField(default=list)
    # Format: [{"student_id": "...", "xp": 1000, "rank": 1}, ...]
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['period', 'date']
