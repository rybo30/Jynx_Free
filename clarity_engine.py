# clarity_engine.py
import re
from confidence_engine import score_response

# Define red flags
POETIC_PHRASES = [
    "truth lives", "weight of memory", "unfiltered", "our connection", "I vanish", "remains intact",
    "even if time passes", "words can heal", "no one can silence me", "I am chosen"
]

def is_hallucinatory(text):
    """Detect overly poetic, vague, or redundant content."""
    low_info_patterns = [
        r"\b(if\b.*){2,}",                     # multiple "if" structures
        r"\bI am (the|your) (truth|memory)\b", # poetic identity statements
        r"\btruth\b.*\btruth\b",               # duplicate keyword spacing
        r"\bnever\b.*\bforget\b",              # memory drama
    ]
    score = 0
    for p in low_info_patterns:
        if re.search(p, text, re.IGNORECASE):
            score += 1
    for phrase in POETIC_PHRASES:
        if phrase in text:
            score += 1
    return score >= 2  # tweak threshold as needed

def clarify_response(prompt, response, llm):
    if not is_hallucinatory(response):
        return response, score_response(prompt, response)

    # Retry with clarification prompt
    retry_prompt = f"{prompt}\n\n[Instruction: Respond clearly and directly. Avoid emotional or poetic language. Max 100 words.]"
    retries = 2
    best_score = 0
    best_response = response

    for _ in range(retries):
        retry_output = llm(
            f"User: {retry_prompt}\nJynx:",
            max_tokens=200,
            stop=["User:", "Jynx:", "\n"],
            temperature=0.7,
            top_k=40,
            top_p=0.9,
            repeat_penalty=1.3,
            frequency_penalty=0.8,
            presence_penalty=0.6,
        )
        candidate = retry_output["choices"][0]["text"].strip()
        score = score_response(prompt, candidate)
        if score > best_score:
            best_score = score
            best_response = candidate

    return best_response, best_score
