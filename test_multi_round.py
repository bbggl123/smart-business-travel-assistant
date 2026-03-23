import requests
import json

def test_multi_round():
    url = "http://localhost:8000/api/chat/stream"
    
    test_cases = [
        {"message": "我想出差", "session_id": "test-multi-1"},
        {"message": "去深圳", "session_id": "test-multi-1"},
        {"message": "我是经理", "session_id": "test-multi-1"},
    ]
    
    for i, data in enumerate(test_cases):
        print(f"\n{'='*50}")
        print(f"Round {i+1}: {data['message']}")
        print('='*50)
        
        response = requests.post(url, json=data, stream=True)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            continue
        
        full_content = ""
        missing_fields = []
        questions = []
        is_complete = False
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data:'):
                    d = json.loads(line[5:])
                    content = d.get('content', '')
                    full_content += content
                    
                    if d.get('missing_fields'):
                        missing_fields = d.get('missing_fields')
                    if d.get('questions'):
                        questions = d.get('questions')
                    if 'is_complete' in d:
                        is_complete = d.get('is_complete')
                    
                    if d.get('type') == 'end':
                        print(f"Content: {full_content[:80]}..." if len(full_content) > 80 else full_content)
                        print(f"Missing fields: {missing_fields}")
                        print(f"Questions count: {len(questions)}")
                        print(f"Is complete: {is_complete}")
    
    print("\n\nAll tests completed!")

if __name__ == "__main__":
    test_multi_round()
