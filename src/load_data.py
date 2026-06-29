import json

CANDIDATES_PATH = "data/candidates.jsonl"

def load_candidates(path=CANDIDATES_PATH):
    candidates = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))
    return candidates

if __name__ == "__main__":
    print("Loading candidates...")
    candidates = load_candidates()
    print(f"Total candidates loaded: {len(candidates)}")
    
    # Quick sanity check
    sample = candidates[0]
    print(f"\nFirst candidate ID: {sample['candidate_id']}")
    print(f"Name: {sample['profile']['anonymized_name']}")
    print(f"Title: {sample['profile']['current_title']}")
    print(f"Years of experience: {sample['profile']['years_of_experience']}")
    print(f"Number of skills: {len(sample['skills'])}")
    print(f"Number of jobs in history: {len(sample['career_history'])}")
    print(f"Open to work: {sample['redrob_signals']['open_to_work_flag']}")
    print(f"Last active: {sample['redrob_signals']['last_active_date']}")