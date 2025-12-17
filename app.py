import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load env variables
load_dotenv()

try:
    from db import get_active_prompt, save_new_prompt
    from ai import generate_reply
    from prompt_editor import generate_improved_prompt, apply_manual_instructions
except ImportError:
    from backend.db import get_active_prompt, save_new_prompt
    from backend.ai import generate_reply
    from backend.prompt_editor import generate_improved_prompt, apply_manual_instructions

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/active-prompt', methods=['GET'])
def get_prompt():
    return jsonify({"prompt": get_active_prompt()})

@app.route('/generate-reply', methods=['POST'])
def handle_generate_reply():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    client_sequence = data.get('clientSequence', '')
    chat_history = data.get('chatHistory', [])
    
    reply = generate_reply(client_sequence, chat_history)
    return jsonify({"aiReply": reply})

@app.route('/improve-ai', methods=['POST'])
def handle_improve_ai():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    client_sequence = data.get('clientSequence', '')
    chat_history = data.get('chatHistory', [])
    consultant_reply = data.get('consultantReply', '')
    
    # 1. Generate prediction with current prompt to see what it would have done
    current_prompt = get_active_prompt()
    predicted_reply = generate_reply(client_sequence, chat_history, specific_prompt=current_prompt)
    
    # 2. Run improver
    updated_prompt = generate_improved_prompt(
        current_prompt, 
        client_sequence, 
        chat_history, 
        consultant_reply, 
        predicted_reply
    )
    
    # 3. Save new prompt
    save_new_prompt(updated_prompt, source="auto_learning")
    
    return jsonify({
        "predictedReply": predicted_reply,
        "updatedPrompt": updated_prompt
    })

@app.route('/improve-ai-manually', methods=['POST'])
def handle_manual_improve():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    instructions = data.get('instructions', '')
    
    current_prompt = get_active_prompt()
    updated_prompt = apply_manual_instructions(current_prompt, instructions)
    
    if updated_prompt.startswith("Error:"):
        return jsonify({"error": updated_prompt}), 429

    save_new_prompt(updated_prompt, source="manual_update")
    
    return jsonify({
        "updatedPrompt": updated_prompt
    })

@app.route('/save-prompt', methods=['POST'])
def handle_save_prompt():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400

    prompt_text = data.get('prompt', '')
    if not prompt_text:
        return jsonify({"error": "Prompt text is empty"}), 400
    
    save_new_prompt(prompt_text, source="direct_edit")
    
    return jsonify({
        "status": "success",
        "updatedPrompt": prompt_text
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
