import sys
sys.modules['bitsandbytes'] = None  # 🔥 disable early before any peft/transformers import

from transformers import AutoModelForCausalLM
from peft import PeftModel
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--base_model", type=str, required=True)
parser.add_argument("--lora_model", type=str, required=True)
parser.add_argument("--output_dir", type=str, required=True)
args = parser.parse_args()

# === Load and Merge ===
base_model = AutoModelForCausalLM.from_pretrained(args.base_model, trust_remote_code=True)
model = PeftModel.from_pretrained(base_model, args.lora_model)
model = model.merge_and_unload()

# === Safely patch generation_config ===
if hasattr(model, "generation_config"):
    gen_config = model.generation_config
    if hasattr(gen_config, "temperature") and hasattr(gen_config, "do_sample"):
        if gen_config.temperature and not gen_config.do_sample:
            print("⚠️ Patching generation_config to enable do_sample")
            gen_config.do_sample = True

# === Save model ===
os.makedirs(args.output_dir, exist_ok=True)
model.save_pretrained(args.output_dir, safe_serialization=True, max_shard_size="2GB")
model.config.save_pretrained(args.output_dir)

print(f"✅ Merged model saved to {args.output_dir}")
