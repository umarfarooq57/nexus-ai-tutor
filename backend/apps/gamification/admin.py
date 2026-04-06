from django.contrib import admin
from .models import XPLevel, Achievement, Badge, StudentGamification, StudentAchievement, StudentBadge, DailyChallenge, Leaderboard

@admin.register(XPLevel)
class XPLevelAdmin(admin.ModelAdmin):
    list_display = ('level', 'title', 'xp_required')
    ordering = ('level',)

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'rarity', 'xp_reward', 'is_hidden')
    list_filter = ('category', 'rarity', 'is_hidden')
    search_fields = ('name', 'description')

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'tier', 'color')
    list_filter = ('category', 'tier')
    search_fields = ('name', 'description')

@admin.register(StudentGamification)
class StudentGamificationAdmin(admin.ModelAdmin):
    list_display = ('student', 'total_xp', 'current_level', 'current_streak', 'total_study_time_minutes')
    search_fields = ('student__user__email',)
    ordering = ('-total_xp',)

@admin.register(StudentAchievement)
class StudentAchievementAdmin(admin.ModelAdmin):
    list_display = ('student_gamification', 'achievement', 'earned_at')
    list_filter = ('earned_at', 'achievement__category')
    search_fields = ('student_gamification__student__user__email', 'achievement__name')

@admin.register(StudentBadge)
class StudentBadgeAdmin(admin.ModelAdmin):
    list_display = ('student_gamification', 'badge', 'tier', 'earned_at')
    list_filter = ('badge__category', 'earned_at')

@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'challenge_type', 'xp_reward')
    list_filter = ('date', 'challenge_type')
    ordering = ('-date',)

@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    list_display = ('period', 'date')
    list_filter = ('period', 'date')
    ordering = ('-date',)
