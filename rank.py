import sys
import csv
import time
sys.path.append(".")

from src.load_data import load_candidates
from src.honeypot import detect_honeypot
from src.fit_scorer import score_fit
from src.availability import score_availability

OUTPUT_PATH = "submission.csv"

def generate_reasoning(candidate, fit_score, avail_score, is_honeypot):
    signals = candidate["redrob_signals"]
    profile = candidate["profile"]
    yoe = profile.get("years_of_experience", 0)
    title = profile.get("current_title", "")
    company = profile.get("current_company", "")
    notice = signals.get("notice_period_days", 0)
    open_to_work = signals.get("open_to_work_flag", False)
    github = signals.get("github_activity_score", -1)
    response_rate = signals.get("recruiter_response_rate", 0)
    last_active = signals.get("last_active_date", "")
    assessments = signals.get("skill_assessment_scores", {})

    if is_honeypot:
        return "Profile contains inconsistencies suggesting data integrity issues; excluded from serious consideration."

    parts = []

    # Fact 1: current role and experience
    parts.append(f"{yoe} years of experience as {title} at {company}.")

    # Fact 2: most recent relevant job from career history
    career = candidate.get("career_history", [])
    if career:
        most_recent = career[0]
        prev_title = most_recent.get("title", "")
        prev_company = most_recent.get("company", "")
        prev_duration = most_recent.get("duration_months", 0)
        if prev_title and prev_company:
            parts.append(f"Most recent role: {prev_title} at {prev_company} ({prev_duration} months).")

    # Fact 3: top skills with real duration
    top_skills = [
        s.get("name", "") for s in candidate.get("skills", [])
        if s.get("duration_months", 0) > 12 and s.get("proficiency") in ["advanced", "expert"]
    ][:3]
    if top_skills:
        parts.append(f"Verified advanced skills: {', '.join(top_skills)}.")

    # Fact 4: assessment scores if any
    strong_assessments = {k: v for k, v in assessments.items() if v > 75}
    if strong_assessments:
        top_assessment = max(strong_assessments, key=strong_assessments.get)
        parts.append(f"Platform assessment: {top_assessment} ({strong_assessments[top_assessment]:.0f}/100).")

    # Fact 5: availability signals
    if open_to_work and notice <= 30:
        parts.append(f"Open to work, {notice}-day notice period.")
    elif not open_to_work:
        parts.append(f"Not marked open to work; {notice}-day notice period.")
    else:
        parts.append(f"Notice period: {notice} days.")

    # Fact 6: engagement
    if github > 70:
        parts.append(f"Active GitHub contributor (score: {github:.0f}/100).")
    if response_rate < 0.3:
        parts.append(f"Low recruiter response rate ({response_rate:.0%}) is a concern.")

    return " ".join(parts)


def rank_candidates(candidates_path="data/candidates.jsonl", output_path=OUTPUT_PATH):
    start = time.time()
    
    print("Loading candidates...")
    candidates = load_candidates(candidates_path)
    print(f"Loaded {len(candidates)} candidates")

    print("Detecting honeypots...")
    honeypot_flags = [detect_honeypot(c)[0] for c in candidates]

    print("Batch scoring fit...")
    print("Scoring fit...")
    fit_scores = [score_fit(c) for c in candidates]

    print("Scoring availability...")
    avail_scores = [score_availability(c) for c in candidates]

    print("Computing final scores...")
    scored = []
    for i, c in enumerate(candidates):
        if honeypot_flags[i]:
            final = 0.01
        else:
            final = fit_scores[i] * avail_scores[i]
        scored.append((c, final, fit_scores[i], avail_scores[i], honeypot_flags[i]))

    scored.sort(key=lambda x: x[1], reverse=True)
    top100 = scored[:100]

    print(f"Writing submission to {output_path}...")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for rank, (c, final_score, fit, avail, is_hp) in enumerate(top100, start=1):
            reasoning = generate_reasoning(c, fit, avail, is_hp)
            writer.writerow([c["candidate_id"], rank, round(final_score, 6), reasoning])

    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f} seconds!")
    print(f"\nTop 5 candidates:")
    for rank, (c, final_score, fit, avail, is_hp) in enumerate(top100[:5], start=1):
        print(f"  #{rank} {c['candidate_id']} | {c['profile']['current_title']} | fit={fit:.3f} avail={avail:.3f} final={final_score:.4f}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", default="data/candidates.jsonl")
    parser.add_argument("--out", default="submission.csv")
    args = parser.parse_args()
    rank_candidates(args.candidates, args.out)