"""
NEXUS AI Tutor - Reinforcement Learning Teaching Agent
Meta-learning agent that learns to teach optimally
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Categorical, Normal
from typing import Dict, Tuple, Optional, List
import numpy as np


class StateEncoder(nn.Module):
    """Encode student state for RL agent"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        # Student profile encoder
        self.profile_encoder = nn.Sequential(
            nn.Linear(config['profile_dim'], config['hidden_dim']),
            nn.ReLU(),
            nn.Linear(config['hidden_dim'], config['hidden_dim'])
        )
        
        # Knowledge graph encoder (GNN-style)
        self.knowledge_encoder = nn.Sequential(
            nn.Linear(config['knowledge_dim'], config['hidden_dim']),
            nn.ReLU(),
            nn.Linear(config['hidden_dim'], config['hidden_dim'])
        )
        
        # Error pattern encoder
        self.error_encoder = nn.Sequential(
            nn.Linear(config['error_dim'], config['hidden_dim'] // 2),
            nn.ReLU(),
            nn.Linear(config['hidden_dim'] // 2, config['hidden_dim'] // 2)
        )
        
        # Temporal encoder for learning history
        self.temporal_encoder = nn.LSTM(
            input_size=config['history_dim'],
            hidden_size=config['hidden_dim'] // 2,
            num_layers=2,
            batch_first=True
        )
        
        # Emotion/cognitive state encoder
        self.emotion_encoder = nn.Sequential(
            nn.Linear(config['emotion_dim'], config['hidden_dim'] // 4),
            nn.ReLU()
        )
        
        # Final fusion
        total_dim = (
            config['hidden_dim'] +  # profile
            config['hidden_dim'] +  # knowledge
            config['hidden_dim'] // 2 +  # errors
            config['hidden_dim'] // 2 +  # temporal
            config['hidden_dim'] // 4   # emotion
        )
        
        self.fusion = nn.Sequential(
            nn.Linear(total_dim, config['state_dim']),
            nn.LayerNorm(config['state_dim']),
            nn.ReLU()
        )
        
    def forward(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Encode full student state
        
        Args:
            state_dict: Dictionary containing:
                - profile: [batch, profile_dim]
                - knowledge: [batch, knowledge_dim]
                - errors: [batch, error_dim]
                - history: [batch, seq_len, history_dim]
                - emotion: [batch, emotion_dim]
        """
        profile_enc = self.profile_encoder(state_dict['profile'])
        knowledge_enc = self.knowledge_encoder(state_dict['knowledge'])
        error_enc = self.error_encoder(state_dict['errors'])
        
        # LSTM for temporal history
        _, (h_n, _) = self.temporal_encoder(state_dict['history'])
        temporal_enc = h_n[-1]  # Last layer hidden state
        
        emotion_enc = self.emotion_encoder(state_dict['emotion'])
        
        # Concatenate all encodings
        combined = torch.cat([
            profile_enc,
            knowledge_enc,
            error_enc,
            temporal_enc,
            emotion_enc
        ], dim=-1)
        
        return self.fusion(combined)


class OptionsCriticNetwork(nn.Module):
    """High-level policy for curriculum selection (Options Framework)"""
    
    def __init__(self, state_dim: int, num_options: int, hidden_dim: int):
        super().__init__()
        
        # Policy over options
        self.option_policy = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_options)
        )
        
        # Option termination conditions
        self.termination_head = nn.Sequential(
            nn.Linear(state_dim + num_options, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Sigmoid()
        )
        
        # Value function for options
        self.option_value = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, num_options)
        )
        
        self.num_options = num_options
        
    def forward(
        self, 
        state: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Select option (curriculum strategy)
        
        Returns:
            option_probs: Probability over options
            option_values: Value for each option
            option: Selected option index
        """
        option_logits = self.option_policy(state)
        option_probs = F.softmax(option_logits, dim=-1)
        option_values = self.option_value(state)
        
        # Sample option
        dist = Categorical(option_probs)
        option = dist.sample()
        
        return option_probs, option_values, option
    
    def get_termination(
        self, 
        state: torch.Tensor, 
        current_option: torch.Tensor
    ) -> torch.Tensor:
        """Check if current option should terminate"""
        option_onehot = F.one_hot(current_option, self.num_options).float()
        combined = torch.cat([state, option_onehot], dim=-1)
        return self.termination_head(combined)


class PPOActorCritic(nn.Module):
    """Low-level PPO policy for specific teaching actions"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int):
        super().__init__()
        
        # Shared feature extractor
        self.shared = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # Actor (policy network)
        # Discrete actions: topic, content_type, style
        self.topic_head = nn.Linear(hidden_dim, action_dim['num_topics'])
        self.content_type_head = nn.Linear(hidden_dim, action_dim['num_content_types'])
        self.style_head = nn.Linear(hidden_dim, action_dim['num_styles'])
        
        # Continuous action: difficulty level
        self.difficulty_mean = nn.Linear(hidden_dim, 1)
        self.difficulty_logstd = nn.Parameter(torch.zeros(1))
        
        # Critic (value network)
        self.value_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        
    def forward(self, state: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Get action distributions and value
        
        Returns dict with:
            - topic_probs
            - content_type_probs  
            - style_probs
            - difficulty_mean, difficulty_std
            - value
        """
        features = self.shared(state)
        
        return {
            'topic_logits': self.topic_head(features),
            'content_type_logits': self.content_type_head(features),
            'style_logits': self.style_head(features),
            'difficulty_mean': torch.sigmoid(self.difficulty_mean(features)),
            'difficulty_std': self.difficulty_logstd.exp(),
            'value': self.value_head(features)
        }
    
    def get_action(self, state: torch.Tensor) -> Dict[str, torch.Tensor]:
        """Sample action from policy"""
        outputs = self.forward(state)
        
        # Sample discrete actions
        topic_dist = Categorical(logits=outputs['topic_logits'])
        content_dist = Categorical(logits=outputs['content_type_logits'])
        style_dist = Categorical(logits=outputs['style_logits'])
        
        topic = topic_dist.sample()
        content_type = content_dist.sample()
        style = style_dist.sample()
        
        # Sample continuous action
        difficulty_dist = Normal(outputs['difficulty_mean'], outputs['difficulty_std'])
        difficulty = difficulty_dist.sample().clamp(0, 1)
        
        return {
            'topic': topic,
            'content_type': content_type,
            'style': style,
            'difficulty': difficulty,
            'value': outputs['value'],
            'log_probs': {
                'topic': topic_dist.log_prob(topic),
                'content_type': content_dist.log_prob(content_type),
                'style': style_dist.log_prob(style),
                'difficulty': difficulty_dist.log_prob(difficulty)
            }
        }
    
    def evaluate_action(
        self, 
        state: torch.Tensor, 
        action: Dict[str, torch.Tensor]
    ) -> Tuple[Dict[str, torch.Tensor], torch.Tensor, torch.Tensor]:
        """Evaluate action for PPO update"""
        outputs = self.forward(state)
        
        topic_dist = Categorical(logits=outputs['topic_logits'])
        content_dist = Categorical(logits=outputs['content_type_logits'])
        style_dist = Categorical(logits=outputs['style_logits'])
        difficulty_dist = Normal(outputs['difficulty_mean'], outputs['difficulty_std'])
        
        log_probs = {
            'topic': topic_dist.log_prob(action['topic']),
            'content_type': content_dist.log_prob(action['content_type']),
            'style': style_dist.log_prob(action['style']),
            'difficulty': difficulty_dist.log_prob(action['difficulty'])
        }
        
        entropy = (
            topic_dist.entropy() + 
            content_dist.entropy() + 
            style_dist.entropy() + 
            0.5 * (1 + torch.log(2 * np.pi * outputs['difficulty_std'] ** 2))
        )
        
        return log_probs, outputs['value'], entropy


class WorldModel(nn.Module):
    """World model for model-based RL (DreamerV3-inspired)"""
    
    def __init__(self, config):
        super().__init__()
        
        # RSSM (Recurrent State Space Model)
        self.rssm_hidden_dim = config['rssm_hidden_dim']
        self.stoch_dim = config['stoch_dim']
        self.deter_dim = config['deter_dim']
        
        # Recurrent model (deterministic path)
        self.rnn = nn.GRUCell(
            input_size=config['state_dim'] + config['action_dim'],
            hidden_size=self.deter_dim
        )
        
        # Prior (predict stochastic state from deterministic)
        self.prior_net = nn.Sequential(
            nn.Linear(self.deter_dim, config['hidden_dim']),
            nn.ReLU(),
            nn.Linear(config['hidden_dim'], self.stoch_dim * 2)  # mean and logvar
        )
        
        # Posterior (refine prediction with observation)
        self.posterior_net = nn.Sequential(
            nn.Linear(self.deter_dim + config['state_dim'], config['hidden_dim']),
            nn.ReLU(),
            nn.Linear(config['hidden_dim'], self.stoch_dim * 2)
        )
        
        # Reward predictor
        self.reward_head = nn.Sequential(
            nn.Linear(self.deter_dim + self.stoch_dim, config['hidden_dim']),
            nn.ReLU(),
            nn.Linear(config['hidden_dim'], 1)
        )
        
        # State predictor (decoder)
        self.state_decoder = nn.Sequential(
            nn.Linear(self.deter_dim + self.stoch_dim, config['hidden_dim']),
            nn.ReLU(),
            nn.Linear(config['hidden_dim'], config['state_dim'])
        )
        
        # Continue predictor (episode termination)
        self.continue_head = nn.Sequential(
            nn.Linear(self.deter_dim + self.stoch_dim, config['hidden_dim']),
            nn.ReLU(),
            nn.Linear(config['hidden_dim'], 1),
            nn.Sigmoid()
        )
        
    def _sample_stochastic(
        self, 
        mean: torch.Tensor, 
        logvar: torch.Tensor
    ) -> torch.Tensor:
        """Reparameterized sampling"""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mean + eps * std
    
    def forward(
        self,
        state: torch.Tensor,
        action: torch.Tensor,
        h: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """
        One step of world model
        
        Args:
            state: Current state observation [batch, state_dim]
            action: Action taken [batch, action_dim]
            h: Previous deterministic state [batch, deter_dim]
        """
        # Recurrent step
        x = torch.cat([state, action], dim=-1)
        h_new = self.rnn(x, h)
        
        # Prior
        prior_params = self.prior_net(h_new)
        prior_mean, prior_logvar = prior_params.chunk(2, dim=-1)
        
        # Posterior (with observation)
        posterior_input = torch.cat([h_new, state], dim=-1)
        posterior_params = self.posterior_net(posterior_input)
        posterior_mean, posterior_logvar = posterior_params.chunk(2, dim=-1)
        
        # Sample stochastic state
        z = self._sample_stochastic(posterior_mean, posterior_logvar)
        
        # Combined state
        combined = torch.cat([h_new, z], dim=-1)
        
        # Predictions
        reward_pred = self.reward_head(combined)
        state_pred = self.state_decoder(combined)
        continue_pred = self.continue_head(combined)
        
        return {
            'h': h_new,
            'z': z,
            'prior_mean': prior_mean,
            'prior_logvar': prior_logvar,
            'posterior_mean': posterior_mean,
            'posterior_logvar': posterior_logvar,
            'reward_pred': reward_pred,
            'state_pred': state_pred,
            'continue_pred': continue_pred
        }
    
    def imagine(
        self,
        initial_state: torch.Tensor,
        initial_h: torch.Tensor,
        policy: nn.Module,
        horizon: int
    ) -> Dict[str, torch.Tensor]:
        """Imagine future trajectories for planning"""
        batch_size = initial_state.size(0)
        
        imagined_states = [initial_state]
        imagined_rewards = []
        h = initial_h
        state = initial_state
        
        for _ in range(horizon):
            # Get action from policy
            action = policy.get_action(state)
            action_tensor = self._encode_action(action)
            
            # Imagine next state
            prior_params = self.prior_net(h)
            prior_mean, prior_logvar = prior_params.chunk(2, dim=-1)
            z = self._sample_stochastic(prior_mean, prior_logvar)
            
            # Recurrent step
            x = torch.cat([state, action_tensor], dim=-1)
            h = self.rnn(x, h)
            
            combined = torch.cat([h, z], dim=-1)
            state = self.state_decoder(combined)
            reward = self.reward_head(combined)
            
            imagined_states.append(state)
            imagined_rewards.append(reward)
        
        return {
            'states': torch.stack(imagined_states, dim=1),
            'rewards': torch.stack(imagined_rewards, dim=1)
        }
    
    def _encode_action(self, action_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Encode action dictionary to tensor"""
        return torch.cat([
            action_dict['topic'].unsqueeze(-1).float(),
            action_dict['content_type'].unsqueeze(-1).float(),
            action_dict['style'].unsqueeze(-1).float(),
            action_dict['difficulty']
        ], dim=-1)


class IntrinsicCuriosity(nn.Module):
    """Random Network Distillation for exploration bonus"""
    
    def __init__(self, state_dim: int, feature_dim: int):
        super().__init__()
        
        # Fixed random network (target)
        self.target_net = nn.Sequential(
            nn.Linear(state_dim, feature_dim),
            nn.ReLU(),
            nn.Linear(feature_dim, feature_dim)
        )
        for param in self.target_net.parameters():
            param.requires_grad = False
        
        # Predictor network (trained to match target)
        self.predictor_net = nn.Sequential(
            nn.Linear(state_dim, feature_dim),
            nn.ReLU(),
            nn.Linear(feature_dim, feature_dim),
            nn.ReLU(),
            nn.Linear(feature_dim, feature_dim)
        )
        
    def get_bonus(self, state: torch.Tensor) -> torch.Tensor:
        """Get intrinsic reward bonus based on prediction error"""
        with torch.no_grad():
            target_features = self.target_net(state)
        
        predicted_features = self.predictor_net(state)
        
        # MSE as curiosity bonus
        bonus = F.mse_loss(predicted_features, target_features, reduction='none')
        return bonus.mean(dim=-1, keepdim=True)
    
    def update(self, state: torch.Tensor) -> torch.Tensor:
        """Update predictor network"""
        with torch.no_grad():
            target_features = self.target_net(state)
        
        predicted_features = self.predictor_net(state)
        loss = F.mse_loss(predicted_features, target_features)
        
        return loss


class MetaTeachingAgent(nn.Module):
    """
    Complete Meta-Learning RL Teaching Agent
    Combines all components for adaptive teaching
    """
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        # State encoder
        self.state_encoder = StateEncoder(config)
        
        # High-level policy (curriculum selection)
        self.options_critic = OptionsCriticNetwork(
            state_dim=config['state_dim'],
            num_options=config['num_curriculum_options'],
            hidden_dim=config['hidden_dim']
        )
        
        # Low-level policy (specific actions)
        self.ppo_policy = PPOActorCritic(
            state_dim=config['state_dim'] + config['num_curriculum_options'],
            action_dim=config['action_dim'],
            hidden_dim=config['hidden_dim']
        )
        
        # World model for planning
        self.world_model = WorldModel(config)
        
        # Intrinsic curiosity
        self.curiosity = IntrinsicCuriosity(
            config['state_dim'],
            config['curiosity_dim']
        )
        
        # MAML-style fast adaptation parameters
        self.adaptation_lr = config.get('adaptation_lr', 0.01)
        self.adaptation_steps = config.get('adaptation_steps', 5)
        
        # Current option tracking
        self.current_option = None
        self.option_start_state = None
        
    def encode_state(self, state_dict: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Encode raw state to latent representation"""
        return self.state_encoder(state_dict)
    
    def select_action(
        self, 
        state: torch.Tensor,
        evaluation: bool = False
    ) -> Dict[str, torch.Tensor]:
        """
        Select teaching action
        
        Args:
            state: Encoded student state [batch, state_dim]
            evaluation: If True, use deterministic policy
        """
        # Check option termination / select new option
        if self.current_option is None:
            option_probs, option_values, option = self.options_critic(state)
            self.current_option = option
            self.option_start_state = state
        else:
            termination_prob = self.options_critic.get_termination(
                state, self.current_option
            )
            if torch.bernoulli(termination_prob).item() > 0.5:
                option_probs, option_values, option = self.options_critic(state)
                self.current_option = option
                self.option_start_state = state
        
        # Combine state with option
        option_onehot = F.one_hot(
            self.current_option, 
            self.config['num_curriculum_options']
        ).float()
        augmented_state = torch.cat([state, option_onehot], dim=-1)
        
        # Get low-level action
        action = self.ppo_policy.get_action(augmented_state)
        
        # Add intrinsic bonus
        curiosity_bonus = self.curiosity.get_bonus(state)
        action['curiosity_bonus'] = curiosity_bonus
        action['option'] = self.current_option
        
        return action
    
    def compute_returns(
        self,
        rewards: torch.Tensor,
        values: torch.Tensor,
        dones: torch.Tensor,
        gamma: float = 0.99,
        gae_lambda: float = 0.95
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Compute GAE returns and advantages"""
        advantages = torch.zeros_like(rewards)
        last_gae = 0
        
        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_value = 0
            else:
                next_value = values[t + 1]
            
            delta = rewards[t] + gamma * next_value * (1 - dones[t]) - values[t]
            advantages[t] = last_gae = delta + gamma * gae_lambda * (1 - dones[t]) * last_gae
        
        returns = advantages + values
        return returns, advantages
    
    def adapt_to_student(
        self, 
        student_data: List[Dict],
        num_steps: int = None
    ):
        """
        Few-shot adaptation to new student (MAML inner loop)
        
        Args:
            student_data: List of (state, action, reward) tuples
            num_steps: Number of gradient steps
        """
        if num_steps is None:
            num_steps = self.adaptation_steps
        
        # Clone policy for adaptation
        adapted_params = {
            name: param.clone() 
            for name, param in self.ppo_policy.named_parameters()
        }
        
        for step in range(num_steps):
            total_loss = 0
            
            for data in student_data:
                state = data['state']
                action = data['action']
                reward = data['reward']
                
                # Forward pass with adapted params
                log_probs, value, _ = self.ppo_policy.evaluate_action(state, action)
                
                # Simple policy gradient loss
                total_log_prob = sum(lp.mean() for lp in log_probs.values())
                loss = -total_log_prob * reward + F.mse_loss(value.squeeze(), reward)
                total_loss += loss
            
            # Manual gradient descent on adapted params
            grads = torch.autograd.grad(total_loss, adapted_params.values())
            adapted_params = {
                name: param - self.adaptation_lr * grad
                for (name, param), grad in zip(adapted_params.items(), grads)
            }
        
        # Update model with adapted params
        for name, param in self.ppo_policy.named_parameters():
            param.data = adapted_params[name]
    
    def imagine_and_plan(
        self,
        state: torch.Tensor,
        horizon: int = 10
    ) -> Dict[str, torch.Tensor]:
        """Use world model to plan future actions"""
        h = torch.zeros(state.size(0), self.config['deter_dim'], device=state.device)
        return self.world_model.imagine(state, h, self.ppo_policy, horizon)
