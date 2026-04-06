"""
NEXUS AI Tutor - ML Inference Server
FastAPI server for ML model inference
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
import torch
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('nexus.ml.inference')

app = FastAPI(
    title="NEXUS ML Inference API",
    description="ML Model Inference Service for AI Tutor",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Request/Response Models
# ============================================

class StudentState(BaseModel):
    student_id: str
    knowledge_embedding: List[float]
    emotional_state: Dict[str, float]
    cognitive_load: float
    attention_level: float
    session_duration: float
    recent_performance: List[float]


class ContentOption(BaseModel):
    content_id: str
    topic_id: str
    difficulty: float
    content_type: str


class TeachingRecommendation(BaseModel):
    action_type: str  # 'continue_topic', 'review_weakness', 'new_topic', 'take_break', 'quiz'
    topic_id: Optional[str]
    difficulty: float
    style: str
    weak_topics: List[str]
    confidence: float
    expected_reward: float


class EmotionInput(BaseModel):
    image_base64: Optional[str]
    audio_features: Optional[List[float]]


class EmotionOutput(BaseModel):
    emotions: Dict[str, float]
    dominant_emotion: str
    engagement_score: float
    cognitive_load: float


class EmbeddingRequest(BaseModel):
    texts: List[str]


class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]
    dimensions: int


# ============================================
# Model Registry
# ============================================

class ModelRegistry:
    """Manages loading and caching of ML models"""
    
    def __init__(self):
        self.models = {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"ML Inference using device: {self.device}")
    
    async def get_model(self, model_name: str):
        """Lazy load models on first use"""
        if model_name not in self.models:
            await self._load_model(model_name)
        return self.models.get(model_name)
    
    async def _load_model(self, model_name: str):
        """Load a specific model"""
        logger.info(f"Loading model: {model_name}")
        
        try:
            if model_name == 'teaching_agent':
                # Load RL teaching agent
                from ml.models.rl_agents import MetaTeachingAgent
                self.models[model_name] = MetaTeachingAgent(
                    state_dim=512,
                    action_dim=10,
                    hidden_dim=256
                ).to(self.device)
                
            elif model_name == 'emotion_detector':
                # Load emotion detection model
                from ml.models.multimodal import EmotionAwareMultimodalNet
                self.models[model_name] = EmotionAwareMultimodalNet(
                    vision_dim=2048,
                    audio_dim=768,
                    text_dim=768,
                    latent_dim=256
                ).to(self.device)
                
            elif model_name == 'embedding':
                # Use sentence-transformers for embeddings
                from sentence_transformers import SentenceTransformer
                self.models[model_name] = SentenceTransformer('all-MiniLM-L6-v2')
                
            logger.info(f"Model {model_name} loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            self.models[model_name] = None


registry = ModelRegistry()


# ============================================
# API Endpoints
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "device": str(registry.device),
        "models_loaded": list(registry.models.keys())
    }


@app.post("/api/teaching-agent/recommend", response_model=TeachingRecommendation)
async def get_teaching_recommendation(
    student_state: StudentState,
    available_content: List[ContentOption]
):
    """
    Get RL teaching agent recommendation for next action
    """
    try:
        # Prepare state tensor
        state_features = (
            student_state.knowledge_embedding[:256] +
            list(student_state.emotional_state.values()) +
            [student_state.cognitive_load, student_state.attention_level] +
            student_state.recent_performance[:10]
        )
        
        # Pad or truncate to expected dimension
        state_features = state_features[:512] + [0.0] * max(0, 512 - len(state_features))
        
        # Get model (will load if not cached)
        model = await registry.get_model('teaching_agent')
        
        if model is None:
            # Fallback to heuristic decision
            return _heuristic_recommendation(student_state, available_content)
        
        # Run inference
        with torch.no_grad():
            state_tensor = torch.tensor([state_features], dtype=torch.float32).to(registry.device)
            action_probs = model.actor(state_tensor)
            action = action_probs.argmax(dim=-1).item()
        
        # Map action to recommendation
        action_map = {
            0: 'continue_topic',
            1: 'continue_topic',
            2: 'review_weakness',
            3: 'review_weakness', 
            4: 'new_topic',
            5: 'new_topic',
            6: 'quiz',
            7: 'quiz',
            8: 'take_break',
            9: 'take_break'
        }
        
        action_type = action_map.get(action, 'continue_topic')
        
        # Determine best content
        best_content = _select_content(available_content, student_state, action_type)
        
        return TeachingRecommendation(
            action_type=action_type,
            topic_id=best_content.topic_id if best_content else None,
            difficulty=best_content.difficulty if best_content else 0.5,
            style='balanced',
            weak_topics=_get_weak_topics(student_state),
            confidence=0.8,
            expected_reward=0.7
        )
        
    except Exception as e:
        logger.error(f"Error in teaching recommendation: {e}")
        return _heuristic_recommendation(student_state, available_content)


def _heuristic_recommendation(
    student_state: StudentState,
    available_content: List[ContentOption]
) -> TeachingRecommendation:
    """Fallback heuristic recommendation"""
    
    # Check for fatigue
    if student_state.session_duration > 3600:  # 1 hour
        return TeachingRecommendation(
            action_type='take_break',
            topic_id=None,
            difficulty=0.5,
            style='balanced',
            weak_topics=[],
            confidence=0.9,
            expected_reward=0.5
        )
    
    # Check cognitive load
    if student_state.cognitive_load > 0.8:
        return TeachingRecommendation(
            action_type='review_weakness',
            topic_id=available_content[0].topic_id if available_content else None,
            difficulty=0.3,
            style='simplified',
            weak_topics=_get_weak_topics(student_state),
            confidence=0.7,
            expected_reward=0.6
        )
    
    # Default: continue
    return TeachingRecommendation(
        action_type='continue_topic',
        topic_id=available_content[0].topic_id if available_content else None,
        difficulty=0.5,
        style='balanced',
        weak_topics=[],
        confidence=0.6,
        expected_reward=0.7
    )


def _select_content(
    content: List[ContentOption],
    state: StudentState,
    action_type: str
) -> Optional[ContentOption]:
    """Select best content based on action type and student state"""
    if not content:
        return None
    
    # Simple selection - would use more sophisticated algorithm
    if action_type == 'review_weakness':
        # Pick easier content
        return min(content, key=lambda x: x.difficulty)
    elif action_type == 'new_topic':
        # Pick medium difficulty
        return min(content, key=lambda x: abs(x.difficulty - 0.5))
    else:
        return content[0]


def _get_weak_topics(state: StudentState) -> List[str]:
    """Extract weak topics from student state"""
    # This would analyze knowledge embedding
    return []


@app.post("/api/emotion/detect", response_model=EmotionOutput)
async def detect_emotion(input_data: EmotionInput):
    """
    Detect emotions from image and/or audio
    """
    try:
        model = await registry.get_model('emotion_detector')
        
        if model is None:
            # Fallback to neutral
            return EmotionOutput(
                emotions={'neutral': 0.7, 'engaged': 0.3},
                dominant_emotion='neutral',
                engagement_score=0.5,
                cognitive_load=0.5
            )
        
        # Process inputs and run inference
        # Placeholder - would actually process image/audio
        
        return EmotionOutput(
            emotions={
                'engaged': 0.6,
                'neutral': 0.2,
                'confused': 0.1,
                'frustrated': 0.1
            },
            dominant_emotion='engaged',
            engagement_score=0.7,
            cognitive_load=0.4
        )
        
    except Exception as e:
        logger.error(f"Error in emotion detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/embeddings", response_model=EmbeddingResponse)
async def generate_embeddings(request: EmbeddingRequest):
    """
    Generate embeddings for text
    """
    try:
        model = await registry.get_model('embedding')
        
        if model is None:
            raise HTTPException(status_code=503, detail="Embedding model not available")
        
        embeddings = model.encode(request.texts, convert_to_numpy=True)
        
        return EmbeddingResponse(
            embeddings=embeddings.tolist(),
            dimensions=embeddings.shape[1]
        )
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/diagram/analyze")
async def analyze_diagram(file: UploadFile = File(...), context: Optional[str] = None):
    """
    Analyze a diagram/image for educational content
    """
    try:
        # Read file
        contents = await file.read()
        
        # Process with image processor
        # Placeholder response
        
        return {
            "image_type": "architecture",
            "components": [
                {"label": "Component A", "confidence": 0.9},
                {"label": "Component B", "confidence": 0.85}
            ],
            "relationships": [
                {"from": "Component A", "to": "Component B", "type": "connects_to"}
            ],
            "description": "Architecture diagram showing system components",
            "educational_content": "This diagram illustrates the relationship between components..."
        }
        
    except Exception as e:
        logger.error(f"Error analyzing diagram: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/video/keyframes")
async def extract_video_keyframes(file: UploadFile = File(...)):
    """
    Extract and analyze keyframes from video
    """
    try:
        # Process video
        # Placeholder response
        
        return {
            "duration": 120.5,
            "keyframes": [
                {"timestamp": 10.0, "description": "Introduction"},
                {"timestamp": 45.0, "description": "Main concept"},
                {"timestamp": 90.0, "description": "Example"}
            ],
            "transcript_summary": "Video covering fundamental concepts...",
            "topics": ["Topic A", "Topic B"]
        }
        
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
