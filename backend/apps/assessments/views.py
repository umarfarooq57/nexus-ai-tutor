"""
Assessments App Views
API endpoints for quizzes, question generation, and results
"""

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
import uuid

from .models import Quiz, Question, QuizAttempt, QuestionResponse, AdaptiveQuizState
from .serializers import (
    QuizSerializer,
    QuizDetailSerializer,
    QuestionSerializer,
    QuizAttemptSerializer,
    QuizResultSerializer
)


class GenerateQuizView(APIView):
    """Generate a personalized quiz"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        topic_id = request.data.get('topic_id')
        num_questions = request.data.get('num_questions', 10)
        quiz_type = request.data.get('type', 'practice')
        
        if not topic_id:
            return Response(
                {'error': 'topic_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create quiz
            quiz = Quiz.objects.create(
                title=f"Auto-generated Quiz - {timezone.now().strftime('%Y-%m-%d')}",
                topic_id=topic_id,
                quiz_type=quiz_type,
                created_by=request.user,
                is_auto_generated=True,
                config={
                    'num_questions': num_questions,
                    'time_limit': num_questions * 60  # 1 min per question
                }
            )
            
            # Generate questions (placeholder - would use AI)
            self._generate_questions(quiz, num_questions)
            
            return Response(
                QuizSerializer(quiz).data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_questions(self, quiz, num_questions):
        """Generate questions for the quiz using AI"""
        # Placeholder - would use LLM for actual generation
        for i in range(num_questions):
            Question.objects.create(
                quiz=quiz,
                question_type='mcq',
                question_text=f"Sample Question {i+1}?",
                correct_answer='a',
                options=['Option A', 'Option B', 'Option C', 'Option D'],
                explanation="This is the explanation...",
                difficulty=0.5,
                order=i
            )


class QuizDetailView(generics.RetrieveAPIView):
    """Get quiz details with questions"""
    serializer_class = QuizDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Quiz.objects.all()


class SubmitQuizView(APIView):
    """Submit quiz answers and get results"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        quiz_id = request.data.get('quiz_id')
        answers = request.data.get('answers', {})
        
        if not quiz_id:
            return Response(
                {'error': 'quiz_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        try:
            student_profile = request.user.student_profile
        except:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create or get attempt
        attempt, created = QuizAttempt.objects.get_or_create(
            quiz=quiz,
            student=student_profile,
            status='in_progress',
            defaults={
                'started_at': timezone.now()
            }
        )
        
        # Grade answers
        correct_count = 0
        total_points = 0
        questions = quiz.questions.all()
        
        for question in questions:
            student_answer = answers.get(str(question.id), '')
            is_correct = self._check_answer(question, student_answer)
            
            if is_correct:
                correct_count += 1
                total_points += question.points
            
            # Record response
            QuestionResponse.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={
                    'student_answer': str(student_answer),
                    'is_correct': is_correct,
                    'time_taken_seconds': 60,  # Placeholder
                    'ai_feedback': self._generate_feedback(question, student_answer, is_correct)
                }
            )
        
        # Update attempt
        score = correct_count / len(questions) if questions else 0
        attempt.score = score
        attempt.ended_at = timezone.now()
        attempt.status = 'completed'
        attempt.total_points = total_points
        attempt.save()
        
        return Response({
            'attempt_id': str(attempt.id),
            'score': score,
            'correct': correct_count,
            'total': len(questions),
            'passed': score >= (quiz.config.get('passing_score', 0.7) if quiz.config else 0.7)
        })
    
    def _check_answer(self, question, student_answer):
        """Check if answer is correct"""
        correct = question.correct_answer
        if isinstance(correct, list):
            return str(student_answer) in [str(c) for c in correct]
        return str(student_answer).lower().strip() == str(correct).lower().strip()
    
    def _generate_feedback(self, question, student_answer, is_correct):
        """Generate AI feedback for the answer"""
        if is_correct:
            return "Correct! Well done."
        return f"Incorrect. The correct answer is: {question.correct_answer}. {question.explanation}"


class QuizResultsView(generics.RetrieveAPIView):
    """Get detailed quiz results"""
    serializer_class = QuizResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'attempt_id'
    
    def get_object(self):
        attempt_id = self.kwargs.get('attempt_id')
        return get_object_or_404(
            QuizAttempt,
            id=attempt_id,
            student__user=self.request.user
        )


class AdaptiveQuizView(APIView):
    """Adaptive quiz using IRT"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Start or continue adaptive quiz"""
        topic_id = request.data.get('topic_id')
        action = request.data.get('action', 'start')  # start, answer, end
        
        try:
            student_profile = request.user.student_profile
        except:
            return Response(
                {'error': 'Student profile not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if action == 'start':
            return self._start_adaptive(student_profile, topic_id)
        elif action == 'answer':
            return self._process_answer(request, student_profile)
        elif action == 'end':
            return self._end_adaptive(student_profile, topic_id)
        
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
    
    def _start_adaptive(self, student, topic_id):
        """Start a new adaptive quiz"""
        state, created = AdaptiveQuizState.objects.get_or_create(
            student=student,
            topic_id=topic_id,
            defaults={
                'estimated_ability': 0.0,
                'questions_answered': 0
            }
        )
        
        if not created:
            # Reset if existing
            state.estimated_ability = 0.0
            state.questions_answered = 0
            state.save()
        
        # Get first question at medium difficulty
        next_question = self._select_next_question(state)
        
        return Response({
            'state_id': str(state.id),
            'estimated_ability': state.estimated_ability,
            'question': QuestionSerializer(next_question).data if next_question else None
        })
    
    def _process_answer(self, request, student):
        """Process answer and get next question"""
        state_id = request.data.get('state_id')
        question_id = request.data.get('question_id')
        answer = request.data.get('answer')
        
        state = get_object_or_404(AdaptiveQuizState, id=state_id)
        question = get_object_or_404(Question, id=question_id)
        
        # Check answer
        is_correct = str(answer).lower().strip() == str(question.correct_answer).lower().strip()
        
        # Update ability estimate using IRT
        state.estimated_ability = self._update_ability(
            state.estimated_ability,
            question.difficulty,
            is_correct
        )
        state.questions_answered += 1
        state.save()
        
        # Get next question or finish
        if state.questions_answered >= 20:  # Max questions
            return Response({
                'finished': True,
                'final_ability': state.estimated_ability,
                'questions_answered': state.questions_answered
            })
        
        next_question = self._select_next_question(state)
        
        return Response({
            'is_correct': is_correct,
            'estimated_ability': state.estimated_ability,
            'question': QuestionSerializer(next_question).data if next_question else None
        })
    
    def _update_ability(self, current_ability, difficulty, is_correct):
        """Update ability estimate using simple IRT"""
        # Simplified IRT update
        expected = 1 / (1 + 2.71828 ** (-(current_ability - difficulty)))
        actual = 1 if is_correct else 0
        
        # Learning rate based on uncertainty
        lr = 0.5
        
        new_ability = current_ability + lr * (actual - expected)
        return max(-3, min(3, new_ability))  # Bound ability
    
    def _select_next_question(self, state):
        """Select next question based on current ability estimate"""
        # Get questions near estimated ability
        questions = Question.objects.filter(
            quiz__topic=state.topic
        ).exclude(
            id__in=state.answered_question_ids or []
        ).order_by('?')[:1]  # Random for now
        
        return questions.first()
    
    def _end_adaptive(self, student, topic_id):
        """End adaptive quiz and return results"""
        state = AdaptiveQuizState.objects.filter(
            student=student,
            topic_id=topic_id
        ).first()
        
        if not state:
            return Response({'error': 'No active quiz'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'final_ability': state.estimated_ability,
            'questions_answered': state.questions_answered,
            'mastery_estimate': (state.estimated_ability + 3) / 6  # Normalize to 0-1
        })
