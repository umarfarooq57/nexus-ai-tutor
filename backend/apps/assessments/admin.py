from django.contrib import admin
from .models import Quiz, Question, QuizAttempt, QuestionResponse, AdaptiveQuizState, AssessmentReport

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0
    ordering = ('order',)

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'quiz_type', 'course', 'topic', 'is_published', 'total_questions')
    list_filter = ('quiz_type', 'is_published', 'difficulty_score')
    search_fields = ('title', 'course__title', 'topic__title')
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'quiz', 'question_type', 'points', 'difficulty_score')
    list_filter = ('question_type', 'difficulty_score')
    search_fields = ('question_text', 'quiz__title')

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'status', 'score', 'passed', 'started_at')
    list_filter = ('status', 'passed', 'started_at')
    search_fields = ('student__user__email', 'quiz__title')

@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'is_correct', 'points_awarded', 'time_spent')
    list_filter = ('is_correct',)
    search_fields = ('attempt__student__user__email', 'question__question_text')

@admin.register(AdaptiveQuizState)
class AdaptiveQuizStateAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'estimated_ability', 'is_converged', 'convergence_threshold')
    readonly_fields = ('attempt',)

@admin.register(AssessmentReport)
class AssessmentReportAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'generated_at', 'generation_model')
    readonly_fields = ('generated_at',)
