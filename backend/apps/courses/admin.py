from django.contrib import admin
from .models import Course, Module, Topic, Content, ContentVersion, Enrollment

class ModuleInline(admin.StackedInline):
    model = Module
    extra = 0
    ordering = ('order',)

class TopicInline(admin.StackedInline):
    model = Topic
    extra = 0
    ordering = ('order',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty', 'is_published', 'enrollment_count', 'average_rating')
    list_filter = ('category', 'difficulty', 'is_published', 'created_at')
    search_fields = ('title', 'description', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]
    ordering = ('-created_at',)

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'is_published', 'total_topics')
    list_filter = ('course', 'is_published')
    search_fields = ('title', 'course__title')
    inlines = [TopicInline]
    ordering = ('course', 'order')

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'content_type', 'is_published', 'difficulty_score')
    list_filter = ('content_type', 'is_published')
    search_fields = ('title', 'module__title', 'module__course__title')
    ordering = ('module', 'order')

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'content_type', 'presentation_style', 'order', 'is_processed')
    list_filter = ('content_type', 'presentation_style', 'is_processed')
    search_fields = ('title', 'topic__title')
    ordering = ('topic', 'order')

@admin.register(ContentVersion)
class ContentVersionAdmin(admin.ModelAdmin):
    list_display = ('content', 'version_number', 'is_active', 'created_at', 'created_by')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'progress_percentage', 'enrolled_at')
    list_filter = ('status', 'enrolled_at')
    search_fields = ('student__user__email', 'course__title')
