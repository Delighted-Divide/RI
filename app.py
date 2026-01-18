import os
import tiktoken
from flask import Flask, render_template, jsonify, send_file, request
from io import BytesIO

app = Flask(__name__)

CHAPTER_FOLDER = 'chapters'
encoding = tiktoken.get_encoding("cl100k_base")

def get_chapter_data(chapter_num):
    filename = f"chapter_{int(chapter_num):04d}.txt"
    filepath = os.path.join(CHAPTER_FOLDER, filename)
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    word_count = len(content.split())
    line_count = len(lines)
    token_count = len(encoding.encode(content))
    
    return {
        "title": lines[0] if lines else f"Chapter {chapter_num}",
        "content": content,
        "word_count": word_count,
        "line_count": line_count,
        "token_count": token_count,
        "chapter_num": chapter_num
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chapters')
def list_chapters():
    files = sorted([f for f in os.listdir(CHAPTER_FOLDER) if f.startswith('chapter_')])
    return jsonify({"count": len(files)})

@app.route('/api/chapter/<int:num>')
def get_chapter(num):
    data = get_chapter_data(num)
    if not data:
        return jsonify({"error": "Chapter not found"}), 404
    return jsonify(data)

@app.route('/api/range', methods=['POST'])
def get_range():
    req_data = request.json
    start = int(req_data.get('start', 1))
    end = int(req_data.get('end', 1))
    
    combined_content = []
    total_words = 0
    total_lines = 0
    total_tokens = 0
    
    for i in range(start, end + 1):
        data = get_chapter_data(i)
        if data:
            combined_content.append(data['content'])
            total_words += data['word_count']
            total_lines += data['line_count']
            total_tokens += data['token_count']
            
    full_text = "\n\n" + "-"*30 + "\n\n"
    full_text = full_text.join(combined_content)
    
    return jsonify({
        "content": full_text,
        "word_count": total_words,
        "line_count": total_lines,
        "token_count": total_tokens
    })

@app.route('/api/download', methods=['POST'])
def download_range():
    req_data = request.json
    start = int(req_data.get('start', 1))
    end = int(req_data.get('end', 1))
    
    combined_content = []
    for i in range(start, end + 1):
        data = get_chapter_data(i)
        if data:
            combined_content.append(data['content'])
            
    full_text = "\n\n" + "="*50 + "\n\n"
    full_text = full_text.join(combined_content)
    
    buffer = BytesIO()
    buffer.write(full_text.encode('utf-8'))
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f'reverend_insanity_{start}_{end}.txt',
        mimetype='text/plain'
    )

if __name__ == '__main__':
    # Render provides a PORT environment variable. We use 5000 as a fallback.
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
