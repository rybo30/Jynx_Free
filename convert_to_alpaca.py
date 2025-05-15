import os
import re
import json

input_dir = r"C:\GhostDrive_REBUILD\Everything_else\datasets\ghostdata_master\scraped_raw"
output_dir = r"C:\GhostDrive_REBUILD\Everything_else\datasets\ghostdata_master\alpaca_ready"
os.makedirs(output_dir, exist_ok=True)

def split_text(text, max_length=500):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) <= max_length:
            current += sentence + " "
        else:
            chunks.append(current.strip())
            current = sentence + " "
    if current:
        chunks.append(current.strip())

    return chunks

# Step 1: Convert all into one big list
all_items = []

for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        filepath = os.path.join(input_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        topic = filename.replace("wiki_", "").replace(".txt", "").replace("_", " ").title()
        chunks = split_text(text)

        for chunk in chunks:
            if len(chunk.strip()) < 50:
                continue
            all_items.append({
                "instruction": f"Explain this about {topic}.",
                "input": "",
                "output": chunk.strip()
            })

# Step 2: Split into 3 equal parts
total = len(all_items)
part_size = total // 3
parts = [
    all_items[:part_size],
    all_items[part_size:part_size*2],
    all_items[part_size*2:]
]

# Step 3: Write to 3 output files
for i, part in enumerate(parts, start=1):
    output_file = os.path.join(output_dir, f"wiki_alpaca_part{i}.jsonl")
    with open(output_file, 'w', encoding='utf-8') as out_f:
        for item in part:
            out_f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"✅ Saved: {output_file} ({len(part)} prompts)")

print(f"\n✅ Finished processing {total} total examples into 3 split files.")
