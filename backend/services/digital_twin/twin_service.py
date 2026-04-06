"""
NEXUS AI Tutor - Digital Twin Service
Manages the cognitive digital twin of each student
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger('nexus.digital_twin')


@dataclass
class CognitiveState:
    """Current cognitive state of the student"""
    knowledge_state: Dict[str, float]  # topic_id -> mastery (0-1)
    working_memory_load: float  # 0-1
    attention_level: float  # 0-1
    emotional_state: Dict[str, float]  # emotion -> intensity
    learning_momentum: float  # -1 to 1
    fatigue_level: float  # 0-1
    estimated_optimal_difficulty: float  # 0-1


@dataclass
class Prediction:
    """A prediction made by the Digital Twin"""
    prediction_type: str
    predicted_value: Any
    confidence: float
    timestamp: datetime
    features_used: List[str]


class DigitalTwinService:
    """
    Digital Twin Service
    Creates and maintains a cognitive model of each student
    for personalized learning optimization
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.forgetting_rate = self.config.get('forgetting_rate', 0.1)
        self.learning_rate = self.config.get('learning_rate', 0.15)
    
    async def get_cognitive_state(self, student_id: str) -> CognitiveState:
        """
        Get current cognitive state of student
        Aggregates all available data into a unified state
        """
        # In production, this would fetch from database
        # and use ML models for estimation
        
        return CognitiveState(
            knowledge_state={},
            working_memory_load=0.5,
            attention_level=0.7,
            emotional_state={
                'engaged': 0.6,
                'frustrated': 0.1,
                'confident': 0.5
            },
            learning_momentum=0.3,
            fatigue_level=0.2,
            estimated_optimal_difficulty=0.55
        )
    
    async def update_knowledge_state(
        self,
        student_id: str,
        topic_id: str,
        performance: float,
        time_spent: float,
        error_types: List[str] = None
    ) -> Dict[str, float]:
        """
        Update knowledge state after a learning interaction
        
        Args:
            student_id: Student identifier
            topic_id: Topic being learned
            performance: Performance score (0-1)
            time_spent: Time spent in seconds
            error_types: Types of errors made
        """
        # Get current state
        current_state = await self.get_cognitive_state(student_id)
        current_mastery = current_state.knowledge_state.get(topic_id, 0.0)
        
        # Calculate mastery update using learning curve
        # Higher performance = more learning, but with diminishing returns
        learning_gain = self.learning_rate * performance * (1 - current_mastery)
        
        # Time factor - more time spent slightly increases learning
        time_factor = min(1.2, 1.0 + (time_spent / 600) * 0.2)  # 10 min = 1.2x
        
        # Error penalty - errors indicate incomplete mastery
        error_penalty = len(error_types) * 0.02 if error_types else 0
        
        new_mastery = min(1.0, current_mastery + learning_gain * time_factor - error_penalty)
        new_mastery = max(0.0, new_mastery)
        
        # Update state (would persist to database)
        logger.info(f"Student {student_id} topic {topic_id}: {current_mastery:.2f} -> {new_mastery:.2f}")
        
        return {
            'previous_mastery': current_mastery,
            'new_mastery': new_mastery,
            'learning_gain': new_mastery - current_mastery
        }
    
    async def apply_forgetting(
        self,
        student_id: str,
        time_elapsed: timedelta
    ) -> Dict[str, float]:
        """
        Apply forgetting curve to all topics
        Called periodically to simulate natural forgetting
        """
        state = await self.get_cognitive_state(student_id)
        
        days_elapsed = time_elapsed.days
        updates = {}
        
        for topic_id, mastery in state.knowledge_state.items():
            # Ebbinghaus forgetting curve: R = e^(-t/S)
            # S = strength, based on repetitions and time
            retention = mastery * (0.85 ** days_elapsed)  # Simplified
            
            if retention < mastery:
                updates[topic_id] = {
                    'before': mastery,
                    'after': retention,
                    'forgotten': mastery - retention
                }
        
        return updates
    
    async def predict_performance(
        self,
        student_id: str,
        topic_id: str,
        difficulty: float
    ) -> Prediction:
        """
        Predict student performance on upcoming content
        """
        state = await self.get_cognitive_state(student_id)
        topic_mastery = state.knowledge_state.get(topic_id, 0.0)
        
        # Simple prediction model
        # In production, use trained neural network
        base_prediction = topic_mastery
        
        # Adjust for difficulty
        difficulty_adjustment = (state.estimated_optimal_difficulty - difficulty) * 0.2
        
        # Adjust for current state
        attention_adjustment = (state.attention_level - 0.5) * 0.1
        fatigue_adjustment = -state.fatigue_level * 0.1
        
        final_prediction = base_prediction + difficulty_adjustment + attention_adjustment + fatigue_adjustment
        final_prediction = max(0.0, min(1.0, final_prediction))
        
        # Confidence based on data availability
        confidence = min(0.9, 0.3 + topic_mastery * 0.6)
        
        return Prediction(
            prediction_type='performance',
            predicted_value=final_prediction,
            confidence=confidence,
            timestamp=datetime.now(),
            features_used=['topic_mastery', 'difficulty', 'attention', 'fatigue']
        )
    
    async def predict_next_best_topic(
        self,
        student_id: str,
        available_topics: List[str]
    ) -> Dict[str, Any]:
        """
        Predict the best next topic for the student to learn
        """
        state = await self.get_cognitive_state(student_id)
        
        topic_scores = []
        
        for topic_id in available_topics:
            mastery = state.knowledge_state.get(topic_id, 0.0)
            
            # Score based on:
            # 1. Not too easy (already mastered)
            # 2. Not too hard (no prerequisites)
            # 3. Matches current cognitive state
            
            # Zone of proximal development - target 0.3-0.7 mastery topics
            zpd_score = 1.0 - abs(mastery - 0.5) * 2
            
            # Match to optimal difficulty
            difficulty_match = 1.0 - abs(state.estimated_optimal_difficulty - mastery)
            
            # Combine scores
            final_score = (zpd_score * 0.5 + difficulty_match * 0.3 + 
                          (1 - state.fatigue_level) * 0.2)
            
            topic_scores.append({
                'topic_id': topic_id,
                'score': final_score,
                'current_mastery': mastery,
                'recommended_difficulty': state.estimated_optimal_difficulty
            })
        
        # Sort by score
        topic_scores.sort(key=lambda x: -x['score'])
        
        return {
            'recommended_topic': topic_scores[0] if topic_scores else None,
            'alternatives': topic_scores[1:3] if len(topic_scores) > 1 else [],
            'reasoning': 'Based on current mastery levels and cognitive state'
        }
    
    async def predict_dropout_risk(self, student_id: str) -> Prediction:
        """
        Predict risk of student disengagement/dropout
        """
        state = await self.get_cognitive_state(student_id)
        
        # Risk factors
        frustration = state.emotional_state.get('frustrated', 0.0)
        engagement = state.emotional_state.get('engaged', 0.5)
        momentum = state.learning_momentum
        fatigue = state.fatigue_level
        
        # Risk score (0-1)
        risk = (
            frustration * 0.3 +
            (1 - engagement) * 0.3 +
            (1 - momentum) * 0.2 +
            fatigue * 0.2
        ) / 0.8  # Normalize
        
        return Prediction(
            prediction_type='dropout_risk',
            predicted_value=risk,
            confidence=0.6,
            timestamp=datetime.now(),
            features_used=['frustration', 'engagement', 'momentum', 'fatigue']
        )
    
    async def suggest_interventions(
        self,
        student_id: str
    ) -> List[Dict[str, Any]]:
        """
        Suggest interventions based on current state
        """
        state = await self.get_cognitive_state(student_id)
        dropout_risk = await self.predict_dropout_risk(student_id)
        
        interventions = []
        
        # Check for high cognitive load
        if state.working_memory_load > 0.8:
            interventions.append({
                'type': 'reduce_complexity',
                'priority': 'high',
                'action': 'Break down current topic into smaller chunks',
                'reason': 'High cognitive load detected'
            })
        
        # Check for frustration
        if state.emotional_state.get('frustrated', 0) > 0.5:
            interventions.append({
                'type': 'difficulty_adjustment',
                'priority': 'high',
                'action': 'Lower difficulty and provide more hints',
                'reason': 'Frustration detected'
            })
        
        # Check for fatigue
        if state.fatigue_level > 0.7:
            interventions.append({
                'type': 'break_suggestion',
                'priority': 'medium',
                'action': 'Suggest a 10-minute break',
                'reason': 'High fatigue level'
            })
        
        # Check for low engagement
        if state.emotional_state.get('engaged', 0.5) < 0.3:
            interventions.append({
                'type': 'engagement_boost',
                'priority': 'medium',
                'action': 'Introduce gamification or interactive content',
                'reason': 'Low engagement detected'
            })
        
        # Check for high dropout risk
        if dropout_risk.predicted_value > 0.6:
            interventions.append({
                'type': 'human_intervention',
                'priority': 'high',
                'action': 'Consider reaching out personally',
                'reason': 'High dropout risk'
            })
        
        return interventions
    
    async def update_emotional_state(
        self,
        student_id: str,
        detected_emotions: Dict[str, float],
        source: str = 'facial'
    ) -> Dict[str, float]:
        """
        Update emotional state from detected emotions
        """
        # Smooth the update using exponential moving average
        alpha = 0.3  # Update rate
        
        state = await self.get_cognitive_state(student_id)
        current_emotions = state.emotional_state.copy()
        
        for emotion, intensity in detected_emotions.items():
            if emotion in current_emotions:
                current_emotions[emotion] = (
                    alpha * intensity + (1 - alpha) * current_emotions[emotion]
                )
            else:
                current_emotions[emotion] = intensity
        
        # Persist update (would save to database)
        logger.info(f"Updated emotional state for {student_id}: {current_emotions}")
        
        return current_emotions
    
    async def get_learning_analytics(
        self,
        student_id: str,
        time_range: timedelta = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive learning analytics for the student
        """
        state = await self.get_cognitive_state(student_id)
        
        return {
            'current_state': {
                'overall_mastery': sum(state.knowledge_state.values()) / max(1, len(state.knowledge_state)),
                'attention_level': state.attention_level,
                'engagement': state.emotional_state.get('engaged', 0.5),
                'optimal_difficulty': state.estimated_optimal_difficulty
            },
            'topic_breakdown': state.knowledge_state,
            'recommendations': await self.predict_next_best_topic(student_id, list(state.knowledge_state.keys())),
            'interventions': await self.suggest_interventions(student_id),
            'predictions': {
                'dropout_risk': (await self.predict_dropout_risk(student_id)).predicted_value
            }
        }
