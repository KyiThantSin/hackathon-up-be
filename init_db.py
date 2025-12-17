import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

db_url = os.environ.get("DATABASE_URL")

def init_db():
    if not db_url:
        print("Error: DATABASE_URL not found.")
        return

    try:
        print("Connecting to database...")
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check if table exists
        cur.execute("SELECT to_regclass('public.system_prompts');")
        exists = cur.fetchone()[0]
        
        if exists:
            print("Table 'system_prompts' already exists.")
        else:
            print("Creating table 'system_prompts'...")
            with open('schema.sql', 'r') as f:
                schema_sql = f.read()
            cur.execute(schema_sql)
            conn.commit()
            print("Table created successfully!")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error initializing DB: {e}")

if __name__ == "__main__":
    init_db()
