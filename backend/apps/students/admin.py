from django.contrib import admin
from .models import StudentProfile, DigitalTwin, TopicMastery, LearningSession, ErrorPattern, BehaviorMetrics, CognitiveEvent, PredictionLog

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'id', 'primary_learning_style', 'overall_mastery', 'current_streak', 'created_at')
    list_filter = ('primary_learning_style', 'created_at')
    search_fields = ('user__email', 'user__username')
    ordering = ('-created_at',)

@admin.register(DigitalTwin)
class DigitalTwinAdmin(admin.ModelAdmin):
    list_display = ('student', 'id', 'last_sync', 'sync_version', 'current_cognitive_load')
    search_fields = ('student__user__email',)
    readonly_fields = ('id', 'last_sync')

@admin.register(TopicMastery)
class TopicMasteryAdmin(admin.ModelAdmin):
    list_display = ('student', 'topic', 'mastery_level', 'confidence_score', 'last_reviewed')
    list_filter = ('mastery_level', 'last_reviewed')
    search_fields = ('student__user__email', 'topic__title')

@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'started_at', 'duration', 'engagement_score')
    list_filter = ('started_at', 'device_type')
    search_fields = ('student__user__email',)
    ordering = ('-started_at',)

@admin.register(ErrorPattern)
class ErrorPatternAdmin(admin.ModelAdmin):
    list_display = ('student', 'error_type', 'topic', 'frequency', 'resolved')
    list_filter = ('error_type', 'resolved', 'first_occurrence')
    search_fields = ('student__user__email', 'error_description')

@admin.register(BehaviorMetrics)
class BehaviorMetricsAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'total_active_time', 'avg_focus_score', 'topics_completed')
    list_filter = ('date',)
    search_fields = ('student__user__email',)
    ordering = ('-date',)

@admin.register(CognitiveEvent)
class CognitiveEventAdmin(admin.ModelAdmin):
    list_display = ('digital_twin', 'event_type', 'occurred_at', 'emotional_valence')
    list_filter = ('event_type', 'occurred_at')
    ordering = ('-occurred_at',)

@admin.register(PredictionLog)
class PredictionLogAdmin(admin.ModelAdmin):
    list_display = ('digital_twin', 'prediction_type', 'confidence', 'accuracy', 'predicted_at')
    list_filter = ('prediction_type', 'predicted_at')
    ordering = ('-predicted_at',)
