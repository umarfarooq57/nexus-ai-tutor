"""
Courses App Serializers
"""

from rest_framework import serializers
from .models import Course, Module, Topic, Content, ContentVersion, Enrollment


class ContentSerializer(serializers.ModelSerializer):
    """Serializer for content items"""
    
    class Meta:
        model = Content
        fields = [
            'id', 'title', 'content_type', 'text_content', 'code_content',
            'code_language', 'image_url', 'video_url', 'duration_seconds',
            'difficulty', 'created_at'
        ]


class TopicSerializer(serializers.ModelSerializer):
    """Serializer for topics with content"""
    contents = ContentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Topic
        fields = [
            'id', 'title', 'description', 'difficulty', 'estimated_time',
            'learning_objectives', 'order', 'contents'
        ]


class ModuleSerializer(serializers.ModelSerializer):
    """Serializer for modules"""
    topics_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 'order', 'estimated_hours',
            'topics_count'
        ]
    
    def get_topics_count(self, obj):
        return obj.topics.count()


class ModuleDetailSerializer(serializers.ModelSerializer):
    """Detailed module serializer with topics"""
    topics = TopicSerializer(many=True, read_only=True)
    
    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 'order', 'estimated_hours', 'topics'
        ]


class CourseSerializer(serializers.ModelSerializer):
    """Basic course serializer for listings"""
    instructor_name = serializers.CharField(source='instructor.username', read_only=True)
    modules_count = serializers.SerializerMethodField()
    enrolled_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'category', 'difficulty_level',
            'estimated_hours', 'thumbnail_url', 'instructor_name',
            'modules_count', 'enrolled_count', 'rating', 'created_at'
        ]
    
    def get_modules_count(self, obj):
        return obj.modules.count()
    
    def get_enrolled_count(self, obj):
        return obj.enrollments.count()


class CourseDetailSerializer(serializers.ModelSerializer):
    """Detailed course serializer"""
    instructor_name = serializers.CharField(source='instructor.username', read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    prerequisites = CourseSerializer(many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'category', 'difficulty_level',
            'estimated_hours', 'thumbnail_url', 'instructor_name',
            'learning_outcomes', 'prerequisites', 'modules',
            'rating', 'is_enrolled', 'created_at'
        ]
    
    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(
                student__user=request.user
            ).exists()
        return False


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for enrollments"""
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            'id', 'course', 'progress_percentage', 'status',
            'enrolled_at', 'completed_at', 'last_accessed'
        ]
