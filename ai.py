import os
import json
import google.generativeai as genai
try:
    from db import get_active_prompt
except ImportError:
    from backend.db import get_active_prompt

# Configure Gemini
if os.environ.get("GEMINI_API_KEY"):
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-flash-latest')



def generate_reply(client_sequence, chat_history, specific_prompt=None):
    """
    Generates a reply using the active prompt (or specific_prompt if provided).
    Returns the text reply.
    """
    if not os.environ.get("GEMINI_API_KEY"):
        return "Error: GEMINI_API_KEY not found. Please check your .env file."
        
    system_prompt = specific_prompt if specific_prompt else get_active_prompt()
    
    # Format history
    history_str = ""
    for msg in chat_history:
        role = msg.get("role", "unknown")
        content = msg.get("message", "")
        history_str += f"{role.upper()}: {content}\n"
        
    full_prompt = f"""
SYSTEM INSTRUCTION:
{system_prompt}

CHAT HISTORY:
{history_str}

CLIENT MESSAGE:
{client_sequence}

Respond in plain JSON only: {{ "reply": "..." }}
"""

    import time
    
    max_retries = 5
    base_delay = 5
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(full_prompt)
            content = response.text
            
            # Clean up code blocks if Gemini mimics them
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "")
            elif content.startswith("```"):
                content = content.replace("```", "")
                
            data = json.loads(content)
            return data.get("reply", "")
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"Rate limit hit. Retrying in {delay}s...")
                time.sleep(delay)
                continue
                
            print(f"Generation error: {e}")
            if attempt == max_retries - 1:
                return "AI busy (Rate Limit). Please wait 1 min."
    return "AI busy (Rate Limit). Please wait 1 min."
