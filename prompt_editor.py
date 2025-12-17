import os
import json
import google.generativeai as genai

# Configure Gemini
if os.environ.get("GEMINI_API_KEY"):
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-flash-latest')



SYSTEM_INSTRUCTION = """
You are an expert AI Prompt Engineer.
Your objective is to IMPROVE a chatbot's system prompt to better mimic a human consultant.

You will be given:
1. The CURRENT SYSTEM PROMPT
2. A TRAINING SAMPLE (Conversation Context + Real Consultant Reply)
3. The AI'S PREDICTED REPLY (generated using the current prompt)

Your Task:
1. Compare the AI's Prediction vs. the Real Reply.
2. Identify differences in tone, formatting, conciseness, specific knowledge, or greeting style.
3. Rewrite the System Prompt to guide the AI to sound more like the Real Consultant.
4. Keep the prompt concise.

Output Must Be JSON:
{
  "prompt": "The fully updated system prompt text..."
}
"""

def generate_improved_prompt(current_prompt, client_sequence, chat_history, real_reply, ai_predicted_reply):
    if not os.environ.get("GEMINI_API_KEY"):
        return current_prompt
        
    # Format context
    history_str = ""
    for msg in chat_history:
        history_str += f"{msg.get('role', '').upper()}: {msg.get('message', '')}\n"
        
    user_content = f"""
SYSTEM ROLE:
{SYSTEM_INSTRUCTION}

=== INPUT DATA ===
=== CURRENT PROMPT ===
{current_prompt}

=== CONTEXT ===
{history_str}
CLIENT: {client_sequence}

=== AI PREDICTION (TO IMPROVE) ===
{ai_predicted_reply}

=== REAL HUMAN REPLY (TARGET) ===
{real_reply}

Please generate the improved system prompt in JSON format.
"""

    try:
        response = model.generate_content(user_content)
        content = response.text
        
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        elif content.startswith("```"):
            content = content.replace("```", "")
            
        result = json.loads(content)
        return result.get("prompt", current_prompt)
        
    except Exception as e:
        print(f"Prompt improvement error: {e}")
        return current_prompt

def apply_manual_instructions(current_prompt, instructions):
    if not os.environ.get("GEMINI_API_KEY"):
        return current_prompt
        
    system = """
You are an AI System Admin. 
Your task is to update a System Prompt based on user instructions.
Keep the core structure if possible, but apply the requested changes.
Return JSON: { "prompt": "..." }
"""
    user = f"""
SYSTEM ROLE:
{system}

CURRENT PROMPT:
{current_prompt}

USER INSTRUCTIONS:
{instructions}

Update the prompt and return JSON.
"""
    import time
    
    max_retries = 5
    base_delay = 5
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(user)
            content = response.text
            
            if content.startswith("```json"):
                content = content.replace("```json", "").replace("```", "")
            elif content.startswith("```"):
                content = content.replace("```", "")

            return json.loads(content).get("prompt", current_prompt)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                print(f"Rate limit hit. Retrying in {delay}s...")
                time.sleep(delay)
                continue
            
            print(f"Manual update error: {e}")
            if attempt == max_retries - 1:
                return "Error: AI busy (Rate Limit). Please wait 1 min."
    
    return current_prompt
