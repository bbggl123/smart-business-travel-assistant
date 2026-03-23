import requests
import json

def test_stream_chat():
    url = "http://localhost:8000/api/chat/stream"
    data = {
        "message": "我想去深圳出差，下周一开始",
        "session_id": "test-1"
    }
    
    print("Testing /api/chat/stream...")
    response = requests.post(url, json=data, stream=True)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return
    
    print("Streaming response:")
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data:'):
                data_str = line[5:]
                try:
                    d = json.loads(data_str)
                    event_type = d.get('type', 'message')
                    content = d.get('content', '')
                    missing_fields = d.get('missing_fields', [])
                    questions = d.get('questions', [])
                    is_complete = d.get('is_complete', False)
                    
                    if event_type == 'end':
                        print(f"\n--- message_end ---")
                        print(f"content: {content[:50]}..." if len(content) > 50 else content)
                        print(f"missing_fields: {missing_fields}")
                        print(f"questions count: {len(questions)}")
                        print(f"is_complete: {is_complete}")
                    else:
                        print(f"content char: {content}", end="", flush=True)
                except json.JSONDecodeError:
                    print(f"\nJSON decode error: {data_str}")
    
    print("\n\nTest completed!")

if __name__ == "__main__":
    test_stream_chat()
