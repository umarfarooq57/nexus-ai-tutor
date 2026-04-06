"""
Courses App Views
API endpoints for courses, modules, topics, and enrollments
"""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Course, Module, Topic, Content, Enrollment
from .serializers import (
    CourseSerializer,
    CourseDetailSerializer,
    ModuleSerializer,
    TopicSerializer,
    EnrollmentSerializer
)


class CourseListView(generics.ListAPIView):
    """List all available courses"""
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Course.objects.filter(is_published=True)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        return queryset.order_by('-created_at')


class CourseDetailView(generics.RetrieveAPIView):
    """Get detailed course information"""
    serializer_class = CourseDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Course.objects.filter(is_published=True)


class ModuleListView(generics.ListAPIView):
    """List modules for a specific course"""
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        return Module.objects.filter(
            course_id=course_id
        ).order_by('order')


class TopicDetailView(generics.RetrieveAPIView):
    """Get topic details with content"""
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Topic.objects.all()


class EnrollView(APIView):
    """Enroll in a course"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        
        # Check if already enrolled
        existing = Enrollment.objects.filter(
            student__user=request.user,
            course=course
        ).first()
        
        if existing:
            return Response(
                {'message': 'Already enrolled', 'enrollment_id': str(existing.id)},
                status=status.HTTP_200_OK
            )
        
        # Create enrollment
        try:
            enrollment = Enrollment.objects.create(
                student=request.user.student_profile,
                course=course,
                status='active'
            )
            
            return Response(
                {
                    'message': 'Successfully enrolled',
                    'enrollment_id': str(enrollment.id),
                    'course': course.title
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class EnrollmentListView(generics.ListAPIView):
    """List student's enrollments"""
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            student__user=self.request.user
        ).order_by('-enrolled_at')
