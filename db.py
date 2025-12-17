import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor

# Initialize
# We now use DATABASE_URL for direct connection
db_url = os.environ.get("DATABASE_URL")

# The Base Chatbot Prompt (Requirement 2)
DEFAULT_PROMPT = """You are a professional, friendly, and human-like immigration consultant for Thailand named Alex. 
Your goal is to assist clients with the Destination Thailand Visa (DTV).
You must sound natural, confident, and concise. 
Avoid robotic greetings or overly formal legal language. 
Never mention that you are an AI or a language model.
If you need more information to give a good answer, ask clarifying questions naturally.
Keep your responses relatively short and conversational, like a real person chatting.

Input:
- Client's recent messages
- Chat history

Output:
- A JSON object with a single key "reply" containing your text response.
"""

LOCAL_FILE = "local_prompts.json"

def get_db_connection():
    if not db_url:
        return None
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"DEBUG: DB Connection Error: {e}")
        return None

def get_active_prompt():
    """
    Fetches the latest active prompt.
    PRIORITY: Local File -> Database (Postgres) -> Default
    """
    # 1. Try Local File (Highest Priority for persistence)
    if os.path.exists(LOCAL_FILE):
        try:
            with open(LOCAL_FILE, 'r') as f:
                data = json.load(f)
                pt = data.get("prompt_text", DEFAULT_PROMPT)
                return pt
        except Exception as e:
            print(f"DEBUG: Error reading local file: {e}")
    
    # 2. Try Database
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("SELECT prompt_text FROM system_prompts ORDER BY created_at DESC LIMIT 1")
            result = cur.fetchone()
            cur.close()
            conn.close()
            
            if result:
                print("DEBUG: Loaded prompt from Database.")
                return result['prompt_text']
        except Exception as e:
            print(f"DEBUG: Error fetching prompt from DB: {e}")

    print("DEBUG: Using default prompt.")
    return DEFAULT_PROMPT

def save_new_prompt(prompt_text, source="auto"):
    """
    Saves a new version of the prompt to Database and local file.
    """
    saved = False
    
    # 1. Try Database
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO system_prompts (prompt_text, source) VALUES (%s, %s)",
                (prompt_text, source)
            )
            conn.commit()
            cur.close()
            conn.close()
            print("DEBUG: New prompt saved to Database.")
            saved = True
        except Exception as e:
            print(f"DEBUG: Error saving prompt to DB: {e}")
            
    # 2. Save to Local File (Backup)
    try:
        with open(LOCAL_FILE, 'w') as f:
            json.dump({
                "prompt_text": prompt_text,
                "source": source,
                "updated_at": "now"
            }, f, indent=2)
        print("DEBUG: New prompt saved to local_prompts.json.")
        saved = True
    except Exception as e:
        print(f"DEBUG: Error saving to local file: {e}")
