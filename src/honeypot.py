from datetime import datetime, date

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return None

def detect_honeypot(candidate):
    flags = []

    # Flag 1: Experience at a company longer than the company has existed
    for job in candidate.get("career_history", []):
        start = parse_date(job.get("start_date"))
        # If duration is suspiciously long vs years_of_experience
        duration_months = job.get("duration_months", 0)
        if duration_months > 600:  # 50+ years at one job
            flags.append("impossible_duration")

    # Flag 2: Expert skill with 0 months used
    for skill in candidate.get("skills", []):
        if skill.get("proficiency") == "expert" and skill.get("duration_months", 1) == 0:
            flags.append("expert_skill_zero_duration")

    # Flag 3: Years of experience impossible given career history
    total_career_months = sum(
        job.get("duration_months", 0) for job in candidate.get("career_history", [])
    )
    stated_years = candidate.get("profile", {}).get("years_of_experience", 0)
    if stated_years > 0 and total_career_months > 0:
        if total_career_months / 12 > stated_years * 2.5:
            flags.append("career_months_exceed_experience")

    # Flag 4: Multiple expert skills with 0 duration
    zero_duration_experts = sum(
        1 for s in candidate.get("skills", [])
        if s.get("proficiency") in ["expert", "advanced"] and s.get("duration_months", 1) == 0
    )
    if zero_duration_experts >= 3:
        flags.append("multiple_expert_zero_duration")

    # Flag 5: Profile completeness 100 but last active over 2 years ago
    last_active = parse_date(candidate.get("redrob_signals", {}).get("last_active_date"))
    completeness = candidate.get("redrob_signals", {}).get("profile_completeness_score", 0)
    if last_active and completeness == 100:
        days_inactive = (date.today() - last_active).days
        if days_inactive > 730:
            flags.append("perfect_profile_never_active")

    is_honeypot = len(flags) >= 2  # needs 2+ flags to be flagged
    return is_honeypot, flags


if __name__ == "__main__":
    import json
    import sys
    sys.path.append(".")
    from src.load_data import load_candidates

    candidates = load_candidates()
    honeypots = []
    for c in candidates:
        is_hp, flags = detect_honeypot(c)
        if is_hp:
            honeypots.append((c["candidate_id"], flags))

    print(f"Honeypots detected: {len(honeypots)}")
    for cid, flags in honeypots[:10]:
        print(f"  {cid}: {flags}")