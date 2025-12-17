import json
import os

def load_data(file_path='conversations.json'):
    base_path = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_path, file_path)
    with open(full_path, 'r') as f:
        data = json.load(f)
    return data

def process_conversations(conversations):
    samples = []
    
    for conv in conversations:
        messages = conv.get('conversation', [])
        if not messages:
            continue
            
        # Group messages by direction
        grouped_blocks = []
        current_block = {
            "role": "client" if messages[0]['direction'] == 'in' else "consultant",
            "messages": [messages[0]['text']]
        }
        
        for i in range(1, len(messages)):
            msg = messages[i]
            role = "client" if msg['direction'] == 'in' else "consultant"
            
            if role == current_block['role']:
                current_block['messages'].append(msg['text'])
            else:
                grouped_blocks.append(current_block)
                current_block = {
                    "role": role,
                    "messages": [msg['text']]
                }
        grouped_blocks.append(current_block)
        
        history = []
        
        for i in range(len(grouped_blocks) - 1):
            block = grouped_blocks[i]
            next_block = grouped_blocks[i+1]
            
            if block['role'] == 'client' and next_block['role'] == 'consultant':
                client_sequence = "\n\n".join(block['messages'])
                consultant_reply = "\n\n".join(next_block['messages'])
                
                samples.append({
                    "clientSequence": client_sequence,
                    "consultantReply": consultant_reply,
                    "chatHistory": list(history)
                })
            
            # Update history
            history.append({
                "role": block['role'],
                "message": "\n\n".join(block['messages'])
            })
            
    return samples

if __name__ == "__main__":
    try:
        data = load_data()
        samples = process_conversations(data)
        print(f"Total samples extracted: {len(samples)}")
        print("\n--- SAMPLE 1 ---")
        if len(samples) > 0: print(json.dumps(samples[0], indent=2))
        print("\n--- SAMPLE 2 ---")
        if len(samples) > 1: print(json.dumps(samples[1], indent=2))
        print("\n--- SAMPLE 3 ---")
        if len(samples) > 2: print(json.dumps(samples[2], indent=2))
    except Exception as e:
        print(f"Error: {e}")
