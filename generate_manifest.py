import os
import json
import tiktoken

encoding = tiktoken.get_encoding("cl100k_base")
CHAPTER_FOLDER = 'chapters'
manifest = {}

files = sorted([f for f in os.listdir(CHAPTER_FOLDER) if f.startswith('chapter_')])

for filename in files:
    chap_num = int(filename.split('_')[1].split('.')[0])
    filepath = os.path.join(CHAPTER_FOLDER, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    words = len(content.split())
    line_count = len(lines)
    tokens = len(encoding.encode(content))
    
    manifest[chap_num] = {
        "title": lines[0] if lines else f"Chapter {chap_num}",
        "words": words,
        "lines": line_count,
        "tokens": tokens,
        "file": filename
    }

with open('manifest.json', 'w', encoding='utf-8') as f:
    json.dump(manifest, f)

print(f"Manifest created with {len(manifest)} chapters.")
