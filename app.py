import streamlit as st
import json
import csv
import io
import sys
sys.path.append(".")

from src.honeypot import detect_honeypot
from src.fit_scorer import score_fit
from src.availability import score_availability

st.set_page_config(page_title="Redrob Ranker", layout="wide")

st.title("Redrob Ranker — Candidate Ranking Sandbox")
st.markdown("""
Upload a small sample of candidates (JSONL format, ≤100 candidates) to see the ranking system run end-to-end.

The system uses a 3-layer approach:
1. **Honeypot detection** — flags impossible profiles
2. **Fit scoring** — career history + skills matched against JD requirements
3. **Availability scoring** — behavioral signals (recency, response rate, notice period)

Final score = Fit × Availability
""")

uploaded_file = st.file_uploader("Upload candidates JSONL file", type=["jsonl"])

if uploaded_file:
    content = uploaded_file.read().decode("utf-8")
    candidates = [json.loads(line) for line in content.splitlines() if line.strip()]

    st.write(f"Loaded {len(candidates)} candidates")

    if st.button("Run Ranking"):
        with st.spinner("Scoring candidates..."):
            results = []
            for c in candidates:
                is_hp, flags = detect_honeypot(c)
                fit = score_fit(c)
                avail = score_availability(c)
                final = 0.01 if is_hp else fit * avail
                results.append({
                    "candidate_id": c["candidate_id"],
                    "name": c["profile"]["anonymized_name"],
                    "title": c["profile"]["current_title"],
                    "fit_score": round(fit, 3),
                    "availability_score": round(avail, 3),
                    "final_score": round(final, 4),
                    "is_honeypot": is_hp,
                })

            results.sort(key=lambda x: x["final_score"], reverse=True)

        st.success(f"Ranked {len(results)} candidates")
        st.dataframe(results, use_container_width=True)

        # Download button
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

        st.download_button(
            "Download ranked CSV",
            data=output.getvalue(),
            file_name="ranked_sample.csv",
            mime="text/csv"
        )
else:
    st.info("Upload a JSONL file to get started. You can use a small sample from candidates.jsonl (first 50-100 lines).")