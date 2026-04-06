"""
NEXUS AI Tutor - Spaced Repetition Engine
Implements SM-2 algorithm variation for optimal learning retention
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import math
import logging

logger = logging.getLogger('nexus.spaced_repetition')


@dataclass
class ReviewItem:
    """An item scheduled for review"""
    item_id: str
    topic_id: str
    item_type: str  # 'concept', 'flashcard', 'quiz'
    content: Dict
    easiness_factor: float  # EF in SM-2
    interval: int  # Days until next review
    repetitions: int  # Number of successful reviews
    next_review: datetime
    last_review: Optional[datetime]
    last_quality: Optional[int]  # 0-5 quality score


@dataclass
class ReviewSession:
    """A review session result"""
    item_id: str
    quality: int  # 0-5 (0-2 = fail, 3-5 = success)
    response_time: float  # seconds
    reviewed_at: datetime
    new_interval: int
    new_easiness: float
    was_correct: bool


class SpacedRepetitionEngine:
    """
    Spaced Repetition Engine using enhanced SM-2 algorithm
    Optimizes review scheduling for maximum retention
    """
    
    # SM-2 constants
    MIN_EASINESS = 1.3
    DEFAULT_EASINESS = 2.5
    MAX_EASINESS = 3.0
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        # Customizable intervals for first reviews
        self.initial_intervals = self.config.get('initial_intervals', [1, 6])
        # Maximum interval (in days)
        self.max_interval = self.config.get('max_interval', 365)
    
    def calculate_next_review(
        self,
        item: ReviewItem,
        quality: int  # 0-5 quality score
    ) -> Tuple[int, float, datetime]:
        """
        Calculate next review date using SM-2 algorithm
        
        Quality scale:
        0 - Complete blackout
        1 - Incorrect, but recognized after seeing answer
        2 - Incorrect, easy to recall after seeing answer  
        3 - Correct with significant difficulty
        4 - Correct after hesitation
        5 - Perfect response
        
        Returns:
            (new_interval, new_easiness, next_review_date)
        """
        # Get current values
        ef = item.easiness_factor
        interval = item.interval
        repetitions = item.repetitions
        
        # Calculate new easiness factor
        new_ef = self._update_easiness(ef, quality)
        
        # Determine if response was successful (quality >= 3)
        is_successful = quality >= 3
        
        if is_successful:
            # Successful review - increase interval
            if repetitions == 0:
                new_interval = self.initial_intervals[0]
            elif repetitions == 1:
                new_interval = self.initial_intervals[1] if len(self.initial_intervals) > 1 else 6
            else:
                new_interval = round(interval * new_ef)
            
            new_repetitions = repetitions + 1
        else:
            # Failed review - reset to beginning
            new_interval = 1
            new_repetitions = 0
        
        # Cap interval at maximum
        new_interval = min(new_interval, self.max_interval)
        
        # Calculate next review date
        next_review = datetime.now() + timedelta(days=new_interval)
        
        return new_interval, new_ef, next_review
    
    def _update_easiness(self, current_ef: float, quality: int) -> float:
        """Update easiness factor based on quality"""
        # SM-2 formula: EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
        new_ef = current_ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        
        # Keep within bounds
        return max(self.MIN_EASINESS, min(new_ef, self.MAX_EASINESS))
    
    def get_due_items(
        self,
        items: List[ReviewItem],
        limit: int = 20,
        include_new: int = 5
    ) -> List[ReviewItem]:
        """
        Get items due for review, prioritized by urgency
        
        Args:
            items: All review items for the student
            limit: Maximum items to return
            include_new: How many new items to include
        """
        now = datetime.now()
        
        # Separate into due, overdue, and new
        overdue = []
        due_today = []
        new_items = []
        
        for item in items:
            if item.repetitions == 0:
                new_items.append(item)
            elif item.next_review <= now:
                days_overdue = (now - item.next_review).days
                if days_overdue > 0:
                    overdue.append((days_overdue, item))
                else:
                    due_today.append(item)
        
        # Sort overdue by how overdue they are (most overdue first)
        overdue.sort(key=lambda x: -x[0])
        overdue_items = [item for _, item in overdue]
        
        # Combine: overdue first, then due today, then new
        result = []
        
        # Add overdue items
        result.extend(overdue_items[:limit])
        remaining = limit - len(result)
        
        # Add due items
        if remaining > 0:
            result.extend(due_today[:remaining])
            remaining = limit - len(result)
        
        # Add some new items
        if remaining > 0 and include_new > 0:
            new_count = min(remaining, include_new)
            result.extend(new_items[:new_count])
        
        return result
    
    def estimate_retention(
        self,
        item: ReviewItem,
        as_of: datetime = None
    ) -> float:
        """
        Estimate current retention probability using forgetting curve
        
        Returns probability (0-1) that item is still remembered
        """
        if item.last_review is None:
            return 0.0
        
        as_of = as_of or datetime.now()
        
        # Days since last review
        days_elapsed = (as_of - item.last_review).days
        
        if days_elapsed <= 0:
            return 1.0
        
        # Use forgetting curve: R = e^(-t/S)
        # Where S is stability (based on easiness and interval)
        stability = item.interval * item.easiness_factor
        
        retention = math.exp(-days_elapsed / stability)
        
        return max(0.0, min(1.0, retention))
    
    def calculate_optimal_schedule(
        self,
        items: List[ReviewItem],
        daily_limit: int = 20,
        days_ahead: int = 7
    ) -> Dict[str, List[str]]:
        """
        Calculate optimal review schedule for upcoming days
        
        Returns dict mapping dates to lists of item IDs
        """
        schedule = {}
        now = datetime.now()
        
        for day_offset in range(days_ahead):
            date = (now + timedelta(days=day_offset)).strftime('%Y-%m-%d')
            date_items = []
            
            for item in items:
                if item.next_review:
                    item_date = item.next_review.strftime('%Y-%m-%d')
                    if item_date == date:
                        date_items.append(item.item_id)
            
            # Limit items per day
            schedule[date] = date_items[:daily_limit]
        
        return schedule
    
    def analyze_learning_efficiency(
        self,
        sessions: List[ReviewSession]
    ) -> Dict[str, float]:
        """
        Analyze learning efficiency from review sessions
        """
        if not sessions:
            return {
                'accuracy': 0.0,
                'avg_quality': 0.0,
                'retention_trend': 0.0,
                'efficiency_score': 0.0
            }
        
        total = len(sessions)
        correct = sum(1 for s in sessions if s.was_correct)
        avg_quality = sum(s.quality for s in sessions) / total
        
        # Calculate retention trend (are scores improving?)
        if len(sessions) >= 2:
            recent = sessions[-len(sessions)//2:]
            older = sessions[:len(sessions)//2]
            recent_avg = sum(s.quality for s in recent) / len(recent)
            older_avg = sum(s.quality for s in older) / len(older)
            trend = recent_avg - older_avg
        else:
            trend = 0.0
        
        # Overall efficiency
        efficiency = (correct / total) * 0.4 + (avg_quality / 5) * 0.4 + (0.5 + trend/5) * 0.2
        
        return {
            'accuracy': correct / total,
            'avg_quality': avg_quality,
            'retention_trend': trend,
            'efficiency_score': efficiency
        }
    
    def suggest_study_focus(
        self,
        items: List[ReviewItem],
        sessions: List[ReviewSession]
    ) -> List[Dict]:
        """
        Suggest topics to focus on based on performance
        """
        # Group by topic
        topic_stats = {}
        
        for item in items:
            topic_id = item.topic_id
            if topic_id not in topic_stats:
                topic_stats[topic_id] = {
                    'topic_id': topic_id,
                    'total_items': 0,
                    'weak_items': 0,
                    'avg_easiness': 0.0,
                    'review_needed': 0
                }
            
            stats = topic_stats[topic_id]
            stats['total_items'] += 1
            stats['avg_easiness'] += item.easiness_factor
            
            if item.easiness_factor < 2.0:
                stats['weak_items'] += 1
            
            if item.next_review and item.next_review <= datetime.now():
                stats['review_needed'] += 1
        
        # Calculate averages and sort by weakness
        suggestions = []
        for topic_id, stats in topic_stats.items():
            if stats['total_items'] > 0:
                stats['avg_easiness'] /= stats['total_items']
                stats['weakness_score'] = (
                    stats['weak_items'] / stats['total_items'] * 0.5 +
                    (3.0 - stats['avg_easiness']) / 3.0 * 0.3 +
                    stats['review_needed'] / stats['total_items'] * 0.2
                )
                suggestions.append(stats)
        
        # Sort by weakness score (highest first)
        suggestions.sort(key=lambda x: -x['weakness_score'])
        
        return suggestions[:5]  # Top 5 topics to focus on
