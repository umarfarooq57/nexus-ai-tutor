"""
NEXUS AI Tutor - Neuromorphic Spiking Neural Networks
Brain-inspired computing for ultra-efficient learning
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple, Optional, Dict
import math


class SpikingNeuron(nn.Module):
    """Leaky Integrate-and-Fire (LIF) Spiking Neuron"""
    
    def __init__(
        self,
        threshold: float = 1.0,
        membrane_leak: float = 0.9,
        reset_mechanism: str = 'subtract'  # 'zero' or 'subtract'
    ):
        super().__init__()
        self.threshold = threshold
        self.membrane_leak = membrane_leak
        self.reset_mechanism = reset_mechanism
        
    def forward(
        self, 
        input_current: torch.Tensor, 
        membrane: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass of LIF neuron
        
        Args:
            input_current: Input current/weights [batch, features]
            membrane: Previous membrane potential [batch, features]
            
        Returns:
            spikes: Output spikes [batch, features]
            membrane: Updated membrane potential [batch, features]
        """
        # Leaky integration
        membrane = self.membrane_leak * membrane + input_current
        
        # Check for spike
        spikes = (membrane >= self.threshold).float()
        
        # Reset mechanism
        if self.reset_mechanism == 'zero':
            membrane = membrane * (1 - spikes)
        else:  # subtract
            membrane = membrane - spikes * self.threshold
            
        return spikes, membrane


class SpikingLinear(nn.Module):
    """Spiking Linear Layer with temporal dynamics"""
    
    def __init__(
        self,
        in_features: int,
        out_features: int,
        threshold: float = 1.0,
        membrane_leak: float = 0.9,
        use_bias: bool = True
    ):
        super().__init__()
        self.linear = nn.Linear(in_features, out_features, bias=use_bias)
        self.neuron = SpikingNeuron(threshold, membrane_leak)
        self.out_features = out_features
        
    def forward(
        self, 
        x: torch.Tensor, 
        membrane: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            x: Input spikes [batch, in_features]
            membrane: Previous membrane state [batch, out_features]
        """
        if membrane is None:
            membrane = torch.zeros(x.size(0), self.out_features, device=x.device)
            
        current = self.linear(x)
        spikes, membrane = self.neuron(current, membrane)
        
        return spikes, membrane


class HebbianPlasticityLayer(nn.Module):
    """Hebbian Learning Layer - "Neurons that fire together, wire together" """
    
    def __init__(
        self,
        in_features: int,
        out_features: int,
        learning_rate: float = 0.01,
        decay: float = 0.001
    ):
        super().__init__()
        self.weights = nn.Parameter(
            torch.randn(out_features, in_features) * 0.01
        )
        self.learning_rate = learning_rate
        self.decay = decay
        
    def forward(self, pre_spikes: torch.Tensor, post_spikes: torch.Tensor) -> torch.Tensor:
        """
        Apply Hebbian update
        
        Args:
            pre_spikes: Pre-synaptic spikes [batch, in_features]
            post_spikes: Post-synaptic spikes [batch, out_features]
        """
        output = F.linear(pre_spikes, self.weights)
        
        if self.training:
            # Hebbian update: Δw = η * pre * post
            # Batch mean for stability
            hebbian_update = torch.einsum(
                'bi,bo->oi', 
                pre_spikes, 
                post_spikes
            ) / pre_spikes.size(0)
            
            with torch.no_grad():
                self.weights.data += self.learning_rate * hebbian_update
                # Weight decay for stability
                self.weights.data *= (1 - self.decay)
                # Keep weights bounded
                self.weights.data.clamp_(-1, 1)
        
        return output


class TemporalSpikeCoder(nn.Module):
    """Encode/Decode between continuous values and spike trains"""
    
    def __init__(
        self,
        num_steps: int = 100,
        encoding_type: str = 'rate'  # 'rate', 'latency', 'phase'
    ):
        super().__init__()
        self.num_steps = num_steps
        self.encoding_type = encoding_type
        
    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """
        Encode continuous values to spike train
        
        Args:
            x: Input values [batch, features] in [0, 1]
            
        Returns:
            spike_train: [batch, time_steps, features]
        """
        batch_size, features = x.shape
        
        if self.encoding_type == 'rate':
            # Rate coding: higher value = higher spike rate
            probs = x.unsqueeze(1).expand(-1, self.num_steps, -1)
            spike_train = torch.bernoulli(probs)
            
        elif self.encoding_type == 'latency':
            # Latency coding: higher value = earlier spike
            spike_times = ((1 - x) * self.num_steps).long()
            spike_train = torch.zeros(batch_size, self.num_steps, features, device=x.device)
            for b in range(batch_size):
                for f in range(features):
                    t = spike_times[b, f].item()
                    if t < self.num_steps:
                        spike_train[b, t, f] = 1.0
                        
        elif self.encoding_type == 'phase':
            # Phase coding using oscillation
            time_points = torch.arange(self.num_steps, device=x.device).float()
            phases = x.unsqueeze(1) * 2 * math.pi
            spike_train = (torch.sin(time_points.view(1, -1, 1) + phases) > 0.9).float()
            
        return spike_train
    
    def decode(self, spike_train: torch.Tensor) -> torch.Tensor:
        """
        Decode spike train to continuous values
        
        Args:
            spike_train: [batch, time_steps, features]
            
        Returns:
            values: [batch, features]
        """
        if self.encoding_type == 'rate':
            return spike_train.mean(dim=1)
        elif self.encoding_type == 'latency':
            # First spike time
            first_spike = (spike_train.cumsum(dim=1) == 1).float().argmax(dim=1)
            return 1 - first_spike.float() / self.num_steps
        else:
            return spike_train.mean(dim=1)


class LateralInhibitionLayer(nn.Module):
    """Winner-Take-All lateral inhibition"""
    
    def __init__(self, num_neurons: int, inhibition_strength: float = 0.5):
        super().__init__()
        self.inhibition_strength = inhibition_strength
        # Lateral inhibition matrix (all-to-all except self)
        inhibition_matrix = torch.ones(num_neurons, num_neurons) * inhibition_strength
        inhibition_matrix.fill_diagonal_(0)
        self.register_buffer('inhibition_matrix', inhibition_matrix)
        
    def forward(self, membrane: torch.Tensor) -> torch.Tensor:
        """
        Apply lateral inhibition
        
        Args:
            membrane: Membrane potentials [batch, neurons]
            
        Returns:
            inhibited_membrane: [batch, neurons]
        """
        # Find winners (top-k or threshold)
        winners = (membrane == membrane.max(dim=-1, keepdim=True).values).float()
        
        # Apply inhibition
        inhibition = F.linear(winners, self.inhibition_matrix)
        inhibited_membrane = membrane - inhibition
        
        return inhibited_membrane


class SpikingTransformerBlock(nn.Module):
    """Spiking version of Transformer attention block"""
    
    def __init__(
        self,
        d_model: int,
        n_heads: int,
        threshold: float = 1.0,
        membrane_leak: float = 0.9,
        dropout: float = 0.1
    ):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads
        
        # Spiking projections
        self.q_linear = SpikingLinear(d_model, d_model, threshold, membrane_leak)
        self.k_linear = SpikingLinear(d_model, d_model, threshold, membrane_leak)
        self.v_linear = SpikingLinear(d_model, d_model, threshold, membrane_leak)
        self.out_linear = SpikingLinear(d_model, d_model, threshold, membrane_leak)
        
        # Feed-forward
        self.ff1 = SpikingLinear(d_model, d_model * 4, threshold, membrane_leak)
        self.ff2 = SpikingLinear(d_model * 4, d_model, threshold, membrane_leak)
        
        # Layer norm (applied to spike counts)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(
        self, 
        x: torch.Tensor,
        membrane_states: Optional[Dict[str, torch.Tensor]] = None
    ) -> Tuple[torch.Tensor, Dict[str, torch.Tensor]]:
        """
        Args:
            x: Input spikes [batch, seq_len, d_model]
            membrane_states: Dict of membrane potentials for each layer
            
        Returns:
            output: Output spikes [batch, seq_len, d_model]
            membrane_states: Updated membrane states
        """
        batch, seq_len, _ = x.shape
        
        if membrane_states is None:
            membrane_states = {}
        
        # Compute Q, K, V for each position
        q_spikes_list, k_spikes_list, v_spikes_list = [], [], []
        
        for pos in range(seq_len):
            q_spike, membrane_states[f'q_{pos}'] = self.q_linear(
                x[:, pos], 
                membrane_states.get(f'q_{pos}')
            )
            k_spike, membrane_states[f'k_{pos}'] = self.k_linear(
                x[:, pos],
                membrane_states.get(f'k_{pos}')
            )
            v_spike, membrane_states[f'v_{pos}'] = self.v_linear(
                x[:, pos],
                membrane_states.get(f'v_{pos}')
            )
            
            q_spikes_list.append(q_spike)
            k_spikes_list.append(k_spike)
            v_spikes_list.append(v_spike)
        
        # Stack and reshape for multi-head attention
        q = torch.stack(q_spikes_list, dim=1)
        k = torch.stack(k_spikes_list, dim=1)
        v = torch.stack(v_spikes_list, dim=1)
        
        # Reshape for multi-head: [batch, seq, heads, head_dim]
        q = q.view(batch, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        k = k.view(batch, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        v = v.view(batch, seq_len, self.n_heads, self.head_dim).transpose(1, 2)
        
        # Spike-based attention (using spike counts as weights)
        attn_weights = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        attn_weights = F.softmax(attn_weights, dim=-1)
        attn_weights = self.dropout(attn_weights)
        
        # Apply attention to values
        attn_output = torch.matmul(attn_weights, v)
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch, seq_len, self.d_model)
        
        # Output projection with spiking
        output_list = []
        for pos in range(seq_len):
            out_spike, membrane_states[f'out_{pos}'] = self.out_linear(
                attn_output[:, pos],
                membrane_states.get(f'out_{pos}')
            )
            output_list.append(out_spike)
        
        output = torch.stack(output_list, dim=1)
        
        # Residual and norm
        x = self.norm1(x + output)
        
        # Feed-forward
        ff_output_list = []
        for pos in range(seq_len):
            ff1_spike, membrane_states[f'ff1_{pos}'] = self.ff1(
                x[:, pos],
                membrane_states.get(f'ff1_{pos}')
            )
            ff2_spike, membrane_states[f'ff2_{pos}'] = self.ff2(
                ff1_spike,
                membrane_states.get(f'ff2_{pos}')
            )
            ff_output_list.append(ff2_spike)
        
        ff_output = torch.stack(ff_output_list, dim=1)
        output = self.norm2(x + ff_output)
        
        return output, membrane_states


class NeuromorphicConceptExplainer(nn.Module):
    """
    Neuromorphic model for explaining concepts
    Uses spiking neural networks for energy-efficient processing
    """
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        # Temporal spike encoder
        self.spike_encoder = TemporalSpikeCoder(
            num_steps=config.get('time_steps', 100),
            encoding_type='rate'
        )
        
        # Input embedding
        self.input_embed = nn.Linear(
            config.get('vocab_size', 50000),
            config.get('d_model', 512)
        )
        
        # Spiking transformer blocks
        self.spiking_blocks = nn.ModuleList([
            SpikingTransformerBlock(
                d_model=config.get('d_model', 512),
                n_heads=config.get('n_heads', 8),
                threshold=config.get('spike_threshold', 1.0),
                membrane_leak=config.get('membrane_leak', 0.9)
            )
            for _ in range(config.get('n_layers', 6))
        ])
        
        # Hebbian plasticity for student adaptation
        self.hebbian_layer = HebbianPlasticityLayer(
            config.get('d_model', 512),
            config.get('d_model', 512),
            learning_rate=config.get('hebbian_lr', 0.01)
        )
        
        # Lateral inhibition for concept selection
        self.lateral_inhibition = LateralInhibitionLayer(
            config.get('d_model', 512)
        )
        
        # Output projection
        self.output_proj = nn.Linear(
            config.get('d_model', 512),
            config.get('vocab_size', 50000)
        )
        
    def forward(
        self,
        input_ids: torch.Tensor,
        student_embedding: Optional[torch.Tensor] = None,
        time_steps: int = 100
    ) -> Dict[str, torch.Tensor]:
        """
        Generate concept explanation using spiking networks
        
        Args:
            input_ids: Input token IDs [batch, seq_len]
            student_embedding: Student cognitive profile [batch, d_model]
            time_steps: Number of simulation time steps
        """
        batch_size, seq_len = input_ids.shape
        
        # Embed input
        x = self.input_embed(F.one_hot(input_ids, self.config.get('vocab_size', 50000)).float())
        
        # Normalize to [0, 1] for spike encoding
        x = torch.sigmoid(x)
        
        # Process through time steps
        accumulated_output = torch.zeros_like(x)
        membrane_states = {}
        
        for t in range(time_steps):
            # Encode current input as spikes
            x_spikes = self.spike_encoder.encode(x)[:, t % self.spike_encoder.num_steps]
            
            # Process through spiking blocks
            for block in self.spiking_blocks:
                x_spikes, membrane_states = block(x_spikes.unsqueeze(1), membrane_states)
                x_spikes = x_spikes.squeeze(1)
            
            # Apply lateral inhibition
            x_spikes = self.lateral_inhibition(x_spikes)
            
            # Accumulate spikes
            accumulated_output += x_spikes.unsqueeze(1).expand(-1, seq_len, -1)
            
            # Apply Hebbian plasticity if training with student context
            if self.training and student_embedding is not None:
                student_spikes = self.spike_encoder.encode(
                    torch.sigmoid(student_embedding)
                )[:, t % self.spike_encoder.num_steps]
                self.hebbian_layer(x_spikes, student_spikes)
        
        # Decode accumulated spikes
        output = accumulated_output / time_steps
        
        # Project to vocabulary
        logits = self.output_proj(output)
        
        return {
            'logits': logits,
            'spike_activity': accumulated_output,
            'final_membrane_states': membrane_states
        }
