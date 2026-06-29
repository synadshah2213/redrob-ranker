import re

# Core technical signals from the JD
STRONG_POSITIVE = [
    "embedding", "embeddings", "retrieval", "vector", "semantic search",
    "ranking", "recommendation", "nlp", "information retrieval",
    "sentence-transformer", "sentence transformer", "faiss", "pinecone",
    "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch",
    "fine-tun", "rag", "rerank", "hybrid search", "dense retrieval",
    "ndcg", "mrr", "a/b test", "evaluation framework", "learning to rank",
    "xgboost", "neural ranking", "bm25", "sparse", "dense",
    "production ml", "deployed", "real users", "at scale",
    "llm", "language model", "transformer", "bert", "gpt"
]

MILD_POSITIVE = [
    "machine learning", "deep learning", "python", "data science",
    "pytorch", "tensorflow", "scikit", "pandas", "numpy",
    "api", "backend", "engineer", "developer", "architect",
    "startup", "product", "platform", "inference", "model serving"
]

NEGATIVE = [
    "computer vision", "cv engineer", "image recognition", "object detection",
    "speech recognition", "robotics", "manufacturing", "accounting",
    "marketing", "sales", "hr manager", "operations manager",
    "customer support", "civil engineer", "mechanical engineer",
    "supply chain", "logistics", "finance manager"
]

SERVICES_COMPANIES = [
    "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini",
    "hcl", "tech mahindra", "hexaware", "mphasis", "l&t infotech"
]

def normalize(text):
    return text.lower() if text else ""

def count_matches(text, terms):
    text = normalize(text)
    return sum(1 for t in terms if t in text)

def is_services_only(candidate):
    companies = [normalize(job.get("company", "")) for job in candidate.get("career_history", [])]
    if not companies:
        return False
    return all(any(s in c for s in SERVICES_COMPANIES) for c in companies)

def score_fit(candidate):
    if is_services_only(candidate):
        return 0.08

    # Build text from career history
    career_parts = []
    for job in candidate.get("career_history", []):
        career_parts.append(job.get("title", ""))
        career_parts.append(job.get("description", ""))
        career_parts.append(job.get("industry", ""))
    career_text = " ".join(career_parts)

    # Skills text — only count skills with real duration
    skill_parts = []
    for skill in candidate.get("skills", []):
        if skill.get("duration_months", 0) > 0:
            skill_parts.append(skill.get("name", ""))
    skills_text = " ".join(skill_parts)

    # Current title
    title = candidate.get("profile", {}).get("current_title", "")
    headline = candidate.get("profile", {}).get("headline", "")
    summary = candidate.get("profile", {}).get("summary", "")

    full_text = f"{title} {headline} {summary} {career_text} {skills_text}"

    # Negative check first
    neg_hits = count_matches(full_text, NEGATIVE)
    if neg_hits >= 2:
        return 0.05

    # Strong positive hits
    strong_hits = count_matches(full_text, STRONG_POSITIVE)
    mild_hits = count_matches(full_text, MILD_POSITIVE)

    # Score formula
    score = min(strong_hits * 0.06 + mild_hits * 0.015, 0.85)

    # Skill assessment bonus — verified scores on platform
    assessments = candidate.get("redrob_signals", {}).get("skill_assessment_scores", {})
    for skill_name, skill_score in assessments.items():
        if any(t in normalize(skill_name) for t in ["python", "ml", "nlp", "data", "ai"]):
            if skill_score > 70:
                score += 0.05

    # YOE adjustment
    yoe = candidate.get("profile", {}).get("years_of_experience", 0)
    if 5 <= yoe <= 9:
        score *= 1.15
    elif yoe < 2:
        score *= 0.5
    elif yoe > 15:
        score *= 0.9

    return min(score, 1.0)