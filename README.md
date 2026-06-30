# Redrob Ranker

AI-powered candidate ranking system for the Redrob Intelligent Candidate Discovery & Ranking Challenge.

## Overview

This system ranks candidates for a Senior AI Engineer role using a 3-layer scoring approach:

1. **Honeypot Detection** — flags candidates with impossible profiles (e.g. expert-level skills with zero usage duration) to avoid ranking fabricated data.
2. **Fit Scoring** — analyzes career history, skills, and platform assessment scores against the job description's actual requirements, not just keyword matching. Penalizes services-only career backgrounds and unrelated technical domains (CV, robotics, etc.) per the JD's explicit guidance.
3. **Availability Scoring** — a behavioral multiplier based on Redrob platform signals: recency of activity, recruiter response rate, notice period, GitHub activity, and verified contact info. A strong on-paper candidate who is inactive or unresponsive is down-weighted accordingly.

Final score = Fit Score × Availability Score, with honeypots forced to near-zero.

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python rank.py --candidates ./data/candidates.jsonl --out ./submission.csv
```

This produces `submission.csv` with the top 100 ranked candidates, including per-candidate reasoning grounded in specific profile facts (companies, verified skills, assessment scores, availability signals).

Runtime: ~15 seconds on a standard CPU-only machine (well within the 5-minute / 16GB constraint).

## Validation

```bash
python data/validate_submission.py submission.csv
```

## Project Structure