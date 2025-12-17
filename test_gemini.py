import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

if os.environ.get("GEMINI_API_KEY"):
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-2.0-flash')

def test_manual_update():
    current_prompt = "You are a helper."
    instructions = "Add the word BANANA to the prompt."
    
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
    try:
        print("Sending request to Gemini...")
        response = model.generate_content(user)
        print(f"Raw Response Text: {response.text}")
        
        content = response.text
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "")
        elif content.startswith("```"):
            content = content.replace("```", "")
            
        data = json.loads(content)
        print(f"Parsed JSON: {data}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_manual_update()
