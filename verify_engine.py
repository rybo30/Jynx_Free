import json
import os
import difflib

# === CONFIG ===
KNOWLEDGE_PATH = "datasets/jynx_knowledge.jsonl"

def load_knowledge():
    try:
        with open(KNOWLEDGE_PATH, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f if line.strip()]
    except Exception as e:
        return []

def similarity_score(a, b):
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

def verify_input(user_query, top_n=5):
    entries = load_knowledge()
    scored = []

    for entry in entries:
        instruction = entry.get("instruction", "")
        output = entry.get("output", "")
        full_text = f"{instruction} {output}"
        score = similarity_score(user_query, full_text)
        if score > 0.2:
            scored.append({
                "instruction": instruction.strip(),
                "output": output.strip(),
                "score": round(score, 3)
            })

    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)
    return ranked[:top_n]
