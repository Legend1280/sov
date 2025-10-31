import json
import numpy as np
from tqdm import tqdm
import os

def add_controlled_noise(embedding, noise_scale=0.025):
    """Add Gaussian noise and renormalize"""
    emb = np.array(embedding)
    noise = np.random.normal(0, noise_scale, emb.shape)
    noisy_emb = emb + noise
    noisy_emb = noisy_emb / np.linalg.norm(noisy_emb)
    return noisy_emb.tolist()

def transform_dataset(input_dir, output_dir, noise_scale=0.025):
    print(f"Loading data from {input_dir}...")
    
    with open(f'{input_dir}/narrative_vecs.json', 'r') as f:
        narrative_data = json.load(f)
    
    print(f"Loaded {len(narrative_data)} samples")
    print(f"Transforming with noise scale: {noise_scale}")
    
    modal_data = []
    temporal_data = []
    role_data = []
    
    for item in tqdm(narrative_data, desc="Transforming"):
        narrative_emb = item['narrative']
        
        modal_emb = add_controlled_noise(narrative_emb, noise_scale)
        temporal_emb = add_controlled_noise(narrative_emb, noise_scale)
        role_emb = add_controlled_noise(narrative_emb, noise_scale)
        
        modal_data.append({
            'id': item['id'],
            'category': item['category'],
            'modal': modal_emb,
            'modality': item.get('modality', 'unknown'),
            'target': narrative_emb
        })
        
        temporal_data.append({
            'id': item['id'],
            'category': item['category'],
            'temporal_vec': temporal_emb,
            'temporal': item.get('temporal', 'present'),
            'target': narrative_emb
        })
        
        role_data.append({
            'id': item['id'],
            'category': item['category'],
            'role_vec': role_emb,
            'role': item.get('role', 'first_person'),
            'target': narrative_emb
        })
    
    print(f"Saving to {output_dir}...")
    os.makedirs(output_dir, exist_ok=True)
    
    with open(f'{output_dir}/modal_vecs.json', 'w') as f:
        json.dump(modal_data, f)
    
    with open(f'{output_dir}/temporal_vecs.json', 'w') as f:
        json.dump(temporal_data, f)
    
    with open(f'{output_dir}/role_vecs.json', 'w') as f:
        json.dump(role_data, f)
    
    with open(f'{output_dir}/narrative_vecs.json', 'w') as f:
        json.dump(narrative_data, f)
    
    print("✅ Transformation complete!")
    
    # Validate
    sample_narrative = np.array(narrative_data[0]['narrative'])
    sample_modal = np.array(modal_data[0]['modal'])
    cos_sim = np.dot(sample_narrative, sample_modal)
    print(f"\nSample cosine similarity: {cos_sim:.4f}")
    
    if 0.85 <= cos_sim <= 0.95:
        print("✅ Diversity looks good!")
    
    return cos_sim

if __name__ == '__main__':
    transform_dataset('./data', './data_transformed', noise_scale=0.025)
