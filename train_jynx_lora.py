import argparse
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
import os
import sys

# === ENVIRONMENT ===
os.environ["TRANSFORMERS_CACHE"] = "/workspace/.cache"
os.environ["HF_HOME"] = "/workspace/.hf"
sys.modules['bitsandbytes'] = None  # Disable bitsandbytes

# === DISABLE HF MODEL CARD ===
def no_card(*args, **kwargs):
    return
PeftModel.create_or_update_model_card = no_card

# === ARGUMENTS ===
parser = argparse.ArgumentParser()
parser.add_argument("--model_name", type=str, required=True)
parser.add_argument("--train_file", type=str, required=True)
parser.add_argument("--output_dir", type=str, required=True)
parser.add_argument("--resume_from_checkpoint", type=str, default=None)
args = parser.parse_args()

# === LOAD TOKENIZER ===
tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token or "<|endoftext|>"

# === LOAD BASE MODEL ===
model = AutoModelForCausalLM.from_pretrained(
    args.model_name,
    device_map="auto",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True
)

# === APPLY LORA ===
peft_config = LoraConfig(
    r=64,
    lora_alpha=128,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)
model = get_peft_model(model, peft_config)

# === LOAD DATA ===
dataset = load_dataset("json", data_files=args.train_file, split="train")

def tokenize(example):
    prompt = f"{example.get('instruction', '')}\n{example.get('input', '')}\n{example.get('output', '')}".strip()
    return tokenizer(prompt, truncation=True, padding="max_length", max_length=512)

dataset = dataset.map(tokenize, batched=False)

# === TRAINING SETUP ===
training_args = TrainingArguments(
    output_dir=args.output_dir,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    num_train_epochs=3,
    learning_rate=2e-4,
    bf16=True,
    logging_steps=10,
    save_strategy="steps",       # ✅ Save every X steps, not epoch
    save_steps=5000,             # ✅ Save every 5000 steps
    save_total_limit=2,          # ✅ Only keep last 2
    lr_scheduler_type="constant",
    report_to="none",
    resume_from_checkpoint=args.resume_from_checkpoint  # ✅ Auto resume
)


# === TRAINER ===
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
)

# === START TRAINING ===
trainer.train(resume_from_checkpoint=args.resume_from_checkpoint)

# === FINAL SAVE ===
def noop(*args, **kwargs): pass
model.create_or_update_model_card = noop

model.save_pretrained(args.output_dir, safe_serialization=True, push_to_hub=False)
tokenizer.save_pretrained(args.output_dir)
