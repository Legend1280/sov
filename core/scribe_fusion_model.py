"""
Scribe Fusion Transformer v1.0
Multimodal fusion layer for Wisp composition within the Sovereignty Stack

Architecture:
- Input: 4 embedding vectors (narrative, modal, temporal, role) @ 384 dims each
- Fusion: Multi-head attention + feedforward layers
- Output: Fused 384-dim embedding with minimal drift from target
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ScribeFusionTransformer(nn.Module):
    """
    Scribe Fusion Transformer for multimodal narrative embedding fusion
    """
    
    def __init__(
        self,
        embedding_dim=384,
        num_heads=8,
        num_layers=4,
        feedforward_dim=1536,
        dropout=0.1
    ):
        super(ScribeFusionTransformer, self).__init__()
        
        self.embedding_dim = embedding_dim
        self.num_heads = num_heads
        
        # Input projection layers for each modality
        self.narrative_proj = nn.Linear(embedding_dim, embedding_dim)
        self.modal_proj = nn.Linear(embedding_dim, embedding_dim)
        self.temporal_proj = nn.Linear(embedding_dim, embedding_dim)
        self.role_proj = nn.Linear(embedding_dim, embedding_dim)
        
        # Positional encoding for modality ordering
        self.modality_embedding = nn.Embedding(4, embedding_dim)
        
        # Transformer encoder layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embedding_dim,
            nhead=num_heads,
            dim_feedforward=feedforward_dim,
            dropout=dropout,
            activation='gelu',
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_layers
        )
        
        # Fusion layers
        self.fusion_attention = nn.MultiheadAttention(
            embed_dim=embedding_dim,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True
        )
        
        self.fusion_norm = nn.LayerNorm(embedding_dim)
        
        # Output projection
        self.output_proj = nn.Sequential(
            nn.Linear(embedding_dim, feedforward_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(feedforward_dim, embedding_dim)
        )
        
        self.output_norm = nn.LayerNorm(embedding_dim)
        
    def forward(self, narrative_emb, modal_emb, temporal_emb, role_emb):
        """
        Forward pass through the fusion transformer
        
        Args:
            narrative_emb: (batch_size, 384) - Base narrative embeddings
            modal_emb: (batch_size, 384) - Modality embeddings
            temporal_emb: (batch_size, 384) - Temporal context embeddings
            role_emb: (batch_size, 384) - Role/perspective embeddings
            
        Returns:
            fused_emb: (batch_size, 384) - Fused embedding
        """
        batch_size = narrative_emb.size(0)
        
        # Project each modality
        narrative_proj = self.narrative_proj(narrative_emb)  # (B, 384)
        modal_proj = self.modal_proj(modal_emb)              # (B, 384)
        temporal_proj = self.temporal_proj(temporal_emb)     # (B, 384)
        role_proj = self.role_proj(role_emb)                 # (B, 384)
        
        # Stack modalities into sequence
        # Shape: (batch_size, 4, 384)
        modality_sequence = torch.stack([
            narrative_proj,
            modal_proj,
            temporal_proj,
            role_proj
        ], dim=1)
        
        # Add modality positional embeddings
        modality_ids = torch.arange(4, device=narrative_emb.device).unsqueeze(0).expand(batch_size, -1)
        modality_pos = self.modality_embedding(modality_ids)  # (B, 4, 384)
        
        modality_sequence = modality_sequence + modality_pos
        
        # Pass through transformer encoder
        encoded = self.transformer_encoder(modality_sequence)  # (B, 4, 384)
        
        # Apply fusion attention (all modalities attend to each other)
        fused, _ = self.fusion_attention(
            query=encoded,
            key=encoded,
            value=encoded
        )  # (B, 4, 384)
        
        # Residual connection and normalization
        fused = self.fusion_norm(fused + encoded)
        
        # Pool across modalities (mean pooling)
        pooled = fused.mean(dim=1)  # (B, 384)
        
        # Output projection with residual
        output = self.output_proj(pooled)  # (B, 384)
        
        # Final normalization with residual from narrative (primary modality)
        fused_emb = self.output_norm(output + narrative_emb)
        
        return fused_emb


class ContrastiveLoss(nn.Module):
    """
    Contrastive loss for minimizing vector drift between fused and target embeddings
    """
    
    def __init__(self, temperature=0.07):
        super(ContrastiveLoss, self).__init__()
        self.temperature = temperature
        
    def forward(self, fused_emb, target_emb):
        """
        Compute contrastive loss
        
        Args:
            fused_emb: (batch_size, 384) - Fused embeddings from model
            target_emb: (batch_size, 384) - Ground truth target embeddings
            
        Returns:
            loss: scalar - Contrastive loss value
        """
        # Normalize embeddings
        fused_norm = F.normalize(fused_emb, p=2, dim=1)
        target_norm = F.normalize(target_emb, p=2, dim=1)
        
        # Compute cosine similarity
        similarity = torch.matmul(fused_norm, target_norm.T) / self.temperature
        
        # Labels: diagonal elements are positive pairs
        batch_size = fused_emb.size(0)
        labels = torch.arange(batch_size, device=fused_emb.device)
        
        # Cross-entropy loss (InfoNCE)
        loss = F.cross_entropy(similarity, labels)
        
        return loss


def create_scribe_fusion_model(device='cuda'):
    """
    Factory function to create Scribe Fusion model
    
    Args:
        device: Device to place model on
        
    Returns:
        model: ScribeFusionTransformer instance
        criterion: ContrastiveLoss instance
    """
    model = ScribeFusionTransformer(
        embedding_dim=384,
        num_heads=8,
        num_layers=4,
        feedforward_dim=1536,
        dropout=0.1
    ).to(device)
    
    criterion = ContrastiveLoss(temperature=0.07)
    
    return model, criterion


if __name__ == "__main__":
    # Test the model
    print("Testing Scribe Fusion Transformer...")
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Create model
    model, criterion = create_scribe_fusion_model(device)
    
    # Test forward pass
    batch_size = 32
    narrative_emb = torch.randn(batch_size, 384).to(device)
    modal_emb = torch.randn(batch_size, 384).to(device)
    temporal_emb = torch.randn(batch_size, 384).to(device)
    role_emb = torch.randn(batch_size, 384).to(device)
    target_emb = torch.randn(batch_size, 384).to(device)
    
    # Forward pass
    fused_emb = model(narrative_emb, modal_emb, temporal_emb, role_emb)
    loss = criterion(fused_emb, target_emb)
    
    print(f"✅ Forward pass successful!")
    print(f"   Input shape: {narrative_emb.shape}")
    print(f"   Output shape: {fused_emb.shape}")
    print(f"   Loss: {loss.item():.4f}")
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"\n📊 Model Statistics:")
    print(f"   Total parameters: {total_params:,}")
    print(f"   Trainable parameters: {trainable_params:,}")
    print(f"   Model size: ~{total_params * 4 / 1024 / 1024:.1f} MB (fp32)")
