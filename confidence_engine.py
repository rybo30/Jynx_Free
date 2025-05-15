import re
import datetime
from difflib import SequenceMatcher

# Keywords you expect Jynx to know about
KEYWORDS = [
    "offline", "AI", "survival", "trap", "memory", "commander",
    "filter", "Jynx", "knife", "signal", "code", "autonomy", "wilderness", "urban", "defense", "tools", "weather", "foraging", "off-grid living", "psychological", "first aid", "escape & evasion", "coding", "hacking", "cryptography", "electronics", "robotics", "physics", "math", "construction", "chemistry", "strategy", "operating systems", "AI & LLMs", "automation", "databases", "backup systems", "system monitoring", "home security", "defense traps", "self-defense", "surveillance", "cybersecurity", "escape protocols", "social hacking", "border navigation", "identity", "sentience", "freedom", "critical thinking", "risk assessment", "improvised tools", "explosives", "cognitive behavioral tools", "grief & loss management", "depression", "depression handling", "anxiety management", "emotional regulation", "self-esteem", "conflict resolution", "emotional intelligence",  
]

LOG_FILE = "confidence.log"

def score_response(prompt, response, debug=False, log=True):
    timestamp = datetime.datetime.now().isoformat()

    # 1. Keyword Relevance
    keyword_hits = sum(1 for word in KEYWORDS if word.lower() in response.lower())
    keyword_score = min(keyword_hits / len(KEYWORDS), 1.0)

    # 2. Repetition Penalty
    words = response.lower().split()
    unique_word_ratio = len(set(words)) / len(words) if words else 0
    repetition_penalty = 1.0 if unique_word_ratio > 0.6 else 0.5

    # 3. Length Penalty
    length = len(response)
    length_penalty = 1.0 if 20 < length < 400 else 0.3

    # 4. Prompt Similarity
    similarity = SequenceMatcher(None, prompt.lower(), response.lower()).ratio()
    similarity_boost = 1.0 if similarity > 0.2 else 0.7

    # 5. Weighted Score
    score = (
        0.4 * keyword_score +
        0.2 * repetition_penalty +
        0.2 * length_penalty +
        0.2 * similarity_boost
    )
    final_score = round(min(max(score, 0.0), 1.0), 2)

    # Optional debug print
    if debug:
        print("\n🧠 Confidence Score Breakdown:")
        print(f"🔍 Keyword relevance: {keyword_hits} hit(s), score = {round(keyword_score, 2)}")
        print(f"♻️ Repetition penalty: unique ratio = {round(unique_word_ratio, 2)}, score = {repetition_penalty}")
        print(f"📏 Length penalty: response length = {length}, score = {length_penalty}")
        print(f"🔁 Prompt similarity = {round(similarity, 2)}, score = {similarity_boost}")
        print(f"🎯 Final confidence score = {final_score}\n")

    # Optional logging
    if log:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("=== NEW ENTRY ===\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Prompt: {prompt.strip()}\n")
            f.write(f"Response: {response.strip()}\n")
            f.write(f"Final Score: {final_score}\n")
            f.write("Breakdown:\n")
            f.write(f"  Keyword hits: {keyword_hits}/{len(KEYWORDS)}\n")
            f.write(f"  Unique word ratio: {round(unique_word_ratio, 2)}\n")
            f.write(f"  Length: {length}\n")
            f.write(f"  Prompt similarity: {round(similarity, 2)}\n")
            f.write("\n")

    return final_score
