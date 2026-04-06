"""
NEXUS AI Tutor - Gamification Service
Business logic for XP, achievements, and rewards
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('nexus.gamification')


@dataclass
class XPEvent:
    """XP earning event"""
    source: str
    amount: int
    multiplier: float = 1.0
    bonus: int = 0
    description: str = ""


@dataclass
class AchievementUnlock:
    """Achievement unlock notification"""
    achievement_id: str
    name: str
    description: str
    icon: str
    xp_earned: int
    rarity: str


# XP Configuration
XP_CONFIG = {
    'lesson_complete': 50,
    'quiz_complete': 30,
    'quiz_perfect': 100,
    'quiz_pass': 20,
    'streak_day': 25,
    'streak_week': 200,
    'streak_month': 1000,
    'first_login_daily': 10,
    'code_run': 5,
    'code_correct': 15,
    'voice_session': 20,
    'report_generated': 30,
    'topic_mastered': 150,
    'course_complete': 500,
    'challenge_complete': 100,
}

# Achievement Definitions
ACHIEVEMENTS = [
    # Streak Achievements
    {'id': 'streak_3', 'name': 'Getting Started', 'icon': '🔥', 'type': 'streak', 'value': 3, 'xp': 50, 'rarity': 'common'},
    {'id': 'streak_7', 'name': 'Week Warrior', 'icon': '🔥', 'type': 'streak', 'value': 7, 'xp': 150, 'rarity': 'common'},
    {'id': 'streak_30', 'name': 'Monthly Master', 'icon': '🔥', 'type': 'streak', 'value': 30, 'xp': 500, 'rarity': 'rare'},
    {'id': 'streak_100', 'name': 'Unstoppable', 'icon': '💎', 'type': 'streak', 'value': 100, 'xp': 2000, 'rarity': 'legendary'},
    
    # Quiz Achievements
    {'id': 'quiz_first', 'name': 'Quiz Taker', 'icon': '📝', 'type': 'quizzes', 'value': 1, 'xp': 25, 'rarity': 'common'},
    {'id': 'quiz_10', 'name': 'Quiz Enthusiast', 'icon': '📝', 'type': 'quizzes', 'value': 10, 'xp': 100, 'rarity': 'common'},
    {'id': 'quiz_perfect_1', 'name': 'Perfect Score!', 'icon': '💯', 'type': 'perfect_quizzes', 'value': 1, 'xp': 100, 'rarity': 'rare'},
    {'id': 'quiz_perfect_10', 'name': 'Perfectionist', 'icon': '💯', 'type': 'perfect_quizzes', 'value': 10, 'xp': 500, 'rarity': 'epic'},
    
    # Learning Achievements
    {'id': 'lesson_first', 'name': 'First Steps', 'icon': '👣', 'type': 'lessons', 'value': 1, 'xp': 25, 'rarity': 'common'},
    {'id': 'lesson_10', 'name': 'Eager Learner', 'icon': '📚', 'type': 'lessons', 'value': 10, 'xp': 100, 'rarity': 'common'},
    {'id': 'lesson_50', 'name': 'Knowledge Seeker', 'icon': '🎓', 'type': 'lessons', 'value': 50, 'xp': 300, 'rarity': 'rare'},
    {'id': 'lesson_100', 'name': 'Scholar', 'icon': '🏆', 'type': 'lessons', 'value': 100, 'xp': 750, 'rarity': 'epic'},
    
    # Time Achievements
    {'id': 'time_1h', 'name': 'First Hour', 'icon': '⏱️', 'type': 'study_hours', 'value': 1, 'xp': 50, 'rarity': 'common'},
    {'id': 'time_10h', 'name': 'Dedicated', 'icon': '⏱️', 'type': 'study_hours', 'value': 10, 'xp': 200, 'rarity': 'rare'},
    {'id': 'time_100h', 'name': 'Committed', 'icon': '⏱️', 'type': 'study_hours', 'value': 100, 'xp': 1000, 'rarity': 'epic'},
    
    # Level Achievements
    {'id': 'level_5', 'name': 'Rising Star', 'icon': '⭐', 'type': 'level', 'value': 5, 'xp': 100, 'rarity': 'common'},
    {'id': 'level_10', 'name': 'Skilled', 'icon': '⭐', 'type': 'level', 'value': 10, 'xp': 250, 'rarity': 'rare'},
    {'id': 'level_25', 'name': 'Expert', 'icon': '🌟', 'type': 'level', 'value': 25, 'xp': 750, 'rarity': 'epic'},
    {'id': 'level_50', 'name': 'Master', 'icon': '👑', 'type': 'level', 'value': 50, 'xp': 2000, 'rarity': 'legendary'},
    
    # Special Achievements
    {'id': 'night_owl', 'name': 'Night Owl', 'icon': '🦉', 'type': 'special', 'value': 'study_after_midnight', 'xp': 50, 'rarity': 'rare'},
    {'id': 'early_bird', 'name': 'Early Bird', 'icon': '🐦', 'type': 'special', 'value': 'study_before_6am', 'xp': 50, 'rarity': 'rare'},
    {'id': 'weekend_warrior', 'name': 'Weekend Warrior', 'icon': '⚔️', 'type': 'special', 'value': 'weekend_study', 'xp': 75, 'rarity': 'common'},
]

# Level Configuration
LEVELS = [
    {'level': 1, 'xp': 0, 'title': 'Novice', 'icon': '🌱'},
    {'level': 2, 'xp': 100, 'title': 'Beginner', 'icon': '🌿'},
    {'level': 3, 'xp': 250, 'title': 'Learner', 'icon': '📖'},
    {'level': 4, 'xp': 500, 'title': 'Student', 'icon': '📚'},
    {'level': 5, 'xp': 1000, 'title': 'Scholar', 'icon': '🎓'},
    {'level': 10, 'xp': 3000, 'title': 'Expert', 'icon': '⭐'},
    {'level': 15, 'xp': 7500, 'title': 'Master', 'icon': '🌟'},
    {'level': 20, 'xp': 15000, 'title': 'Grandmaster', 'icon': '💫'},
    {'level': 25, 'xp': 30000, 'title': 'Legend', 'icon': '👑'},
    {'level': 50, 'xp': 100000, 'title': 'Mythic', 'icon': '🏆'},
]


class GamificationService:
    """
    Gamification Service
    Handles XP, achievements, and rewards
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.xp_config = XP_CONFIG
        self.achievements = ACHIEVEMENTS
        self.levels = LEVELS
    
    def award_xp(
        self,
        student_id: str,
        source: str,
        multiplier: float = 1.0,
        bonus: int = 0
    ) -> XPEvent:
        """
        Award XP to a student
        """
        base_xp = self.xp_config.get(source, 10)
        total_xp = int(base_xp * multiplier) + bonus
        
        event = XPEvent(
            source=source,
            amount=total_xp,
            multiplier=multiplier,
            bonus=bonus,
            description=f"Earned {total_xp} XP from {source}"
        )
        
        logger.info(f"Student {student_id}: {event.description}")
        
        return event
    
    def check_achievements(
        self,
        student_id: str,
        stats: Dict[str, Any]
    ) -> List[AchievementUnlock]:
        """
        Check if student has unlocked any new achievements
        """
        unlocked = []
        earned_ids = stats.get('earned_achievement_ids', [])
        
        for achievement in self.achievements:
            if achievement['id'] in earned_ids:
                continue
            
            if self._check_condition(achievement, stats):
                unlock = AchievementUnlock(
                    achievement_id=achievement['id'],
                    name=achievement['name'],
                    description=f"Reached {achievement['value']} {achievement['type']}",
                    icon=achievement['icon'],
                    xp_earned=achievement['xp'],
                    rarity=achievement['rarity']
                )
                unlocked.append(unlock)
        
        return unlocked
    
    def _check_condition(self, achievement: Dict, stats: Dict) -> bool:
        """Check if achievement condition is met"""
        condition_type = achievement['type']
        required_value = achievement['value']
        
        if condition_type == 'streak':
            return stats.get('current_streak', 0) >= required_value
        elif condition_type == 'quizzes':
            return stats.get('total_quizzes', 0) >= required_value
        elif condition_type == 'perfect_quizzes':
            return stats.get('perfect_quizzes', 0) >= required_value
        elif condition_type == 'lessons':
            return stats.get('total_lessons', 0) >= required_value
        elif condition_type == 'study_hours':
            return stats.get('total_study_hours', 0) >= required_value
        elif condition_type == 'level':
            return stats.get('level', 1) >= required_value
        elif condition_type == 'special':
            return stats.get(f'special_{required_value}', False)
        
        return False
    
    def get_level_info(self, total_xp: int) -> Dict:
        """Get level information based on XP"""
        current_level = self.levels[0]
        next_level = self.levels[1] if len(self.levels) > 1 else None
        
        for i, level in enumerate(self.levels):
            if total_xp >= level['xp']:
                current_level = level
                next_level = self.levels[i + 1] if i + 1 < len(self.levels) else None
            else:
                break
        
        progress = 0
        if next_level:
            xp_in_level = total_xp - current_level['xp']
            xp_needed = next_level['xp'] - current_level['xp']
            progress = (xp_in_level / xp_needed) * 100
        
        return {
            'level': current_level['level'],
            'title': current_level['title'],
            'icon': current_level['icon'],
            'total_xp': total_xp,
            'progress': progress,
            'xp_to_next': next_level['xp'] - total_xp if next_level else 0,
            'next_level': next_level['level'] if next_level else None
        }
    
    def get_daily_challenges(self, date: datetime = None) -> List[Dict]:
        """Get daily challenges"""
        if date is None:
            date = datetime.now()
        
        # Generate deterministic challenges based on date
        day_of_week = date.weekday()
        
        challenges = [
            {
                'id': f'daily_{date.strftime("%Y%m%d")}_1',
                'title': 'Complete 3 lessons',
                'description': 'Complete any 3 lessons today',
                'type': 'lessons',
                'target': 3,
                'xp_reward': 150,
                'icon': '📚'
            },
            {
                'id': f'daily_{date.strftime("%Y%m%d")}_2',
                'title': 'Score 80%+ on a quiz',
                'description': 'Get at least 80% on any quiz',
                'type': 'quiz_score',
                'target': 80,
                'xp_reward': 100,
                'icon': '🎯'
            },
            {
                'id': f'daily_{date.strftime("%Y%m%d")}_3',
                'title': 'Study for 30 minutes',
                'description': 'Spend 30 minutes learning',
                'type': 'study_time',
                'target': 30,
                'xp_reward': 75,
                'icon': '⏱️'
            }
        ]
        
        # Weekend bonus challenge
        if day_of_week >= 5:
            challenges.append({
                'id': f'daily_{date.strftime("%Y%m%d")}_bonus',
                'title': 'Weekend Bonus!',
                'description': 'Complete all daily challenges',
                'type': 'all_complete',
                'target': 3,
                'xp_reward': 200,
                'icon': '🎁'
            })
        
        return challenges
    
    def get_leaderboard(
        self,
        period: str = 'weekly',
        limit: int = 10
    ) -> List[Dict]:
        """
        Get leaderboard for a period
        """
        # Would fetch from database in production
        # Returning mock data
        return [
            {'rank': 1, 'student_id': 'student1', 'name': 'Top Learner', 'xp': 5000, 'level': 15},
            {'rank': 2, 'student_id': 'student2', 'name': 'Star Student', 'xp': 4500, 'level': 14},
            {'rank': 3, 'student_id': 'student3', 'name': 'Quick Mind', 'xp': 4000, 'level': 13},
        ][:limit]
    
    def calculate_streak_bonus(self, streak: int) -> float:
        """Calculate XP multiplier based on streak"""
        if streak >= 30:
            return 2.0  # 100% bonus
        elif streak >= 14:
            return 1.5  # 50% bonus
        elif streak >= 7:
            return 1.25  # 25% bonus
        elif streak >= 3:
            return 1.1  # 10% bonus
        return 1.0


# Global instance
gamification_service = GamificationService()
