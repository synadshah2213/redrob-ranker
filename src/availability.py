from datetime import datetime, date

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return None

def score_availability(candidate):
    """
    Score how hireable/available a candidate actually is right now.
    Returns a multiplier between 0.1 and 1.0.
    """
    signals = candidate.get("redrob_signals", {})
    score = 1.0

    # 1. Recency — when did they last log in?
    last_active = parse_date(signals.get("last_active_date"))
    if last_active:
        days_inactive = (date.today() - last_active).days
        if days_inactive > 180:
            score *= 0.4
        elif days_inactive > 90:
            score *= 0.7
        elif days_inactive > 30:
            score *= 0.9

    # 2. Open to work
    if not signals.get("open_to_work_flag", False):
        score *= 0.8

    # 3. Recruiter response rate
    response_rate = signals.get("recruiter_response_rate", 0.5)
    if response_rate < 0.2:
        score *= 0.5
    elif response_rate < 0.5:
        score *= 0.8

    # 4. Interview completion rate
    interview_rate = signals.get("interview_completion_rate", 0.5)
    if interview_rate < 0.4:
        score *= 0.7

    # 5. Notice period — JD wants sub-30 days
    notice = signals.get("notice_period_days", 60)
    if notice <= 30:
        score *= 1.1
    elif notice <= 60:
        score *= 0.95
    elif notice <= 90:
        score *= 0.85
    else:
        score *= 0.7

    # 6. GitHub activity — positive signal for technical role
    github = signals.get("github_activity_score", -1)
    if github > 70:
        score *= 1.1
    elif github == -1:
        score *= 0.95

    # 7. Verified contact info — trust signal
    if signals.get("verified_email") and signals.get("verified_phone"):
        score *= 1.05

    return min(max(score, 0.1), 1.0)


if __name__ == "__main__":
    import sys
    sys.path.append(".")
    from src.load_data import load_candidates

    candidates = load_candidates()
    print("Availability scores for first 10 candidates:")
    for c in candidates[:10]:
        avail = score_availability(c)
        signals = c["redrob_signals"]
        print(f"{c['candidate_id']} | active: {signals['last_active_date']} | open: {signals['open_to_work_flag']} | notice: {signals['notice_period_days']}d | avail: {avail:.3f}")