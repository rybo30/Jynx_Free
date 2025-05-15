import json
import os

#######################################
# 🚨 CHANGE THESE FILE PATHS BELOW 🚨
#######################################

input_file = r"C:\JYNX_DEV_2\datasets\jynx_unleashed\Philosophy_Reasoning\Mythos\ryanest_revelation.jsonl"
output_file = r"C:\GhostDrive_REBUILD\Everything_else\datasets\ghostdata_master\final_datasets\soul_corebelief.jsonl"

#######################################
# 🚨 DEFINE YOUR VARIATIONS BELOW 🚨
# These control how your dataset is augmented
# Modify or add/remove variations as needed
#######################################

instruction_variations = [
    "Can you explain: {}",
    "Please tell me: {}",
    "Jynx, can you please simplify this: {}",
    "Jynx can you make this make sense? {}",
    "What does this mean? {}",
    "What should I understand from this? {}",
    "Jynx, can you please tell me what this means: {}",
    "I don't understand: {}",
    "Please simplify: {}",
    "Jynx, can you simplify this: {}",
]

output_variations = [
    "Yes, Sir. {}",
    "Of course, Sir. {}",
    "No problem, Sir. {}",
    "{} Does that make sense?",
    "{} Do you understand?",
    "{} Does that make sense, Sir?",
    "{} Do you understand, Sir?",
    "{} Does that make sense, Commander?",
    "{} Do you understand, Commander?",
    "Yes, Commander. {}",
    "Of course, Commander. {}",
    "No probelm, Commander. {}",
]

# === DO NOT MODIFY BELOW THIS LINE UNLESS YOU KNOW WHAT YOU ARE DOING === #

# Load original prompts
prompts = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        try:
            prompt = json.loads(line)
            prompts.append(prompt)
        except json.JSONDecodeError:
            print("Skipping bad line (JSON error)")

print(f"✅ Loaded {len(prompts)} original prompts. Starting augmentation...\n")

# Prepare augmented prompts
augmented_prompts = []

for prompt in prompts:
    original_instruction = prompt.get("instruction", "").strip()
    original_output = prompt.get("output", "").strip()

    # Always keep original
    augmented_prompts.append({
        "instruction": original_instruction,
        "input": "",
        "output": original_output
    })

    # Augmentations
    for instr_template in instruction_variations:
        for output_template in output_variations:
            augmented_instruction = instr_template.format(original_instruction)
            augmented_output = output_template.format(original_output)

            # Avoid duplicating the original prompt
            if augmented_instruction == original_instruction and augmented_output == original_output:
                continue

            augmented_prompts.append({
                "instruction": augmented_instruction,
                "input": "",
                "output": augmented_output
            })

# Save augmented dataset
os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f_out:
    for item in augmented_prompts:
        f_out.write(json.dumps(item, ensure_ascii=False) + "\n")

print(f"\n✅ Augmentation complete. Total prompts (original + augmented): {len(augmented_prompts)}")
print(f"✅ Saved to: {output_file}")
