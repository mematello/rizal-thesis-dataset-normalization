import pandas as pd
import sys

CANDIDATES_FILE = "residual_candidates.csv"
MAPPING_FILE = "mapping_proposal.csv"

def compile_mappings():
    try:
        df = pd.read_csv(CANDIDATES_FILE)
    except FileNotFoundError:
        print("Candidates file not found.")
        return

    mappings = []
    
    # Approval Logic
    # Approve SAFE items
    # Approve HIGH confidence items (even if frequency is low, if the pattern is strong)
    
    for _, row in df.iterrows():
        status = "REJECTED"
        decision = "PENDING"
        
        if row['auto_action'] == 'SAFE':
            status = "APPROVED"
            decision = "AUTO_SAFE"
        elif row['confidence'] == 'HIGH':
            status = "APPROVED"
            decision = "AUTO_HIGH_CONF"
        
        if status == "APPROVED":
            mappings.append({
                'old_token': row['token'],
                'new_token': row['modern_suggestion'],
                'frequency': row['frequency'],
                'confidence': row['confidence'],
                'reason': row['pattern_match'],
                'reviewer_decision': status,
                'decision_note': decision
            })
            
    mapping_df = pd.DataFrame(mappings)
    
    # Validation
    # 1. Check for duplicates in old_token
    # (Should not happen if candidates list is unique by token)
    if mapping_df['old_token'].duplicated().any():
        print("WARNING: Duplicate source tokens found!")
        mapping_df = mapping_df.drop_duplicates(subset=['old_token'])
        
    # 2. Check for Cycles (A->B and B->A)
    # create dict
    map_dict = dict(zip(mapping_df['old_token'], mapping_df['new_token']))
    
    to_remove = []
    for old, new in map_dict.items():
        if new in map_dict and map_dict[new] == old:
            print(f"CYCLE DETECTED: {old} <-> {new}")
            to_remove.append(old)
            to_remove.append(new)
            
    # 3. Check for Chains (A->B->C)
    for old, new in map_dict.items():
        if new in map_dict:
            # Chain found.
            # Fix chain: A->C
            final = map_dict[new]
            # Avoid infinite loop if cycle exists (handled above but be safe)
            if final == old: continue 
            
            print(f"CHAIN DETECTED: {old} -> {new} -> {final}. resolving to {old} -> {final}")
            # we can update the mapping in the dataframe?
            # actually we should probably flatten it or flag it.
            # Plan says: "No chains unless explicitly approved (A->B->C should be A->C)"
            # So we resolve A->C
            mapping_df.loc[mapping_df['old_token'] == old, 'new_token'] = final
            
    # Remove cycles
    if to_remove:
        mapping_df = mapping_df[~mapping_df['old_token'].isin(to_remove)]
        
    # 4. Collision Check?
    # Ensure no multiple old_tokens map to same new_token? No, that's allowed (cain->kain, cayam->kain? no).
    # Multiple sources to one target is fine (many-to-one).
    # One source to many targets is impossible by design of dict.
    
    print(f"Compiled {len(mapping_df)} approved mappings.")
    mapping_df.to_csv(MAPPING_FILE, index=False)
    print(f"Saved to {MAPPING_FILE}")

if __name__ == "__main__":
    compile_mappings()
