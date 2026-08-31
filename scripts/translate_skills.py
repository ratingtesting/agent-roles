#!/usr/bin/env python3
"""Batch translate SKILL.md from Russian to English using local HF model."""
import re, time, json, torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

root = Path('C:/Projects/agent-roles')
CHECKPOINT = root / '.translate_checkpoint.json'

model_name = "Helsinki-NLP/opus-mt-ru-en"
print(f"Loading model {model_name}...", flush=True)
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def translate_text(text):
    if not text.strip():
        return text
    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=512, num_beams=4)
        return tokenizer.decode(outputs[0], skip_special_tokens=True)
    except Exception as e:
        print(f"  WARN: {e}", flush=True)
        return text

def process_skill(skill_path):
    txt = skill_path.read_text(encoding='utf-8', errors='ignore')
    m = re.match(r'^(---\n.*?\n---\n)(.*)$', txt, re.DOTALL)
    if not m:
        return False
    front_matter = m.group(1)
    body = m.group(2)
    if not re.search(r'[а-яё]', body, re.IGNORECASE):
        return False
    lines = body.split('\n')
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if re.match(r'##\s+(.+)', stripped):
            new_lines.append(line)
            continue
        is_bullet = stripped.startswith('- ')
        is_numbered = bool(re.match(r'^\d+\.\s', stripped))
        if is_bullet:
            content = stripped[2:]
            if re.search(r'[а-яё]', content, re.IGNORECASE):
                translated = translate_text(content)
                new_lines.append(f"- {translated}")
                continue
        elif is_numbered:
            mo = re.match(r'^(\d+\.\s)', stripped)
            marker = mo.group(1)
            content = stripped[len(marker):]
            if re.search(r'[а-яё]', content, re.IGNORECASE):
                translated = translate_text(content)
                new_lines.append(f"{marker}{translated}")
                continue
        if re.search(r'[а-яё]', stripped, re.IGNORECASE) and stripped and not stripped.startswith('```'):
            translated = translate_text(stripped)
            new_lines.append(translated)
        else:
            new_lines.append(line)
    new_body = '\n'.join(new_lines)
    if new_body != body:
        skill_path.write_text(front_matter + new_body, encoding='utf-8')
        return True
    return False

# Load checkpoint
done = []
if CHECKPOINT.exists():
    done = json.loads(CHECKPOINT.read_text())

files = sorted(root.rglob('SKILL.md'))
count = 0
errors = []
print(f"Total files: {len(files)}, already done: {len(done)}", flush=True)

for i, p in enumerate(files):
    rel = str(p.relative_to(root))
    if rel in done:
        continue
    try:
        if process_skill(p):
            count += 1
        done.append(rel)
        if (i + 1) % 20 == 0:
            CHECKPOINT.write_text(json.dumps(done))
            print(f"Progress: {count} translated, {len(done)}/{len(files)} processed", flush=True)
    except Exception as e:
        errors.append((rel, str(e)))
        done.append(rel)
    CHECKPOINT.write_text(json.dumps(done))

print(f'\nTranslated: {count}', flush=True)
print(f'Total processed: {len(done)}', flush=True)
if errors:
    for f, e in errors[:5]:
        print(f'  {f}: {e[:100]}')
