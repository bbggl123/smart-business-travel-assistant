"""
前后端集成测试脚本
测试聊天流、意图理解、消息重复等关键功能
"""
import asyncio
import httpx
import sys
import subprocess
from typing import Tuple

BASE_URL = "http://localhost:8000"

class IntegrationTest:
    def __init__(self):
        self.session_id = f"test_{int(asyncio.get_event_loop().time() * 1000)}"
        self.messages_sent = 0
        self.messages_received = 0
        self.errors = []
        
    async def test_stream_chat(self, message: str, round_num: int) -> Tuple[bool, str]:
        """测试流式聊天接口"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                url = f"{BASE_URL}/api/chat/stream"
                payload = {
                    "message": message,
                    "session_id": self.session_id
                }
                
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        error_msg = f"Round {round_num}: HTTP {response.status_code}"
                        self.errors.append(error_msg)
                        return False, error_msg
                    
                    full_content = ""
                    message_count = 0
                    has_message_end = False
                    missing_fields = []
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            try:
                                import json
                                data = json.loads(line[5:])
                                
                                if "content" in data and data["content"]:
                                    full_content += data["content"]
                                    message_count += 1
                                
                                if data.get("type") == "end":
                                    has_message_end = True
                                    if "missing_fields" in data:
                                        missing_fields = data["missing_fields"]
                                        print(f"  Missing fields: {missing_fields}")
                                    if "questions" in data:
                                        print(f"  Questions count: {len(data.get('questions', []))}")
                                    if "is_complete" in data:
                                        print(f"  Is complete: {data.get('is_complete')}")
                                    
                            except Exception as e:
                                pass
                    
                    self.messages_received += 1
                    
                    if message_count == 0:
                        error_msg = f"Round {round_num}: No content received"
                        self.errors.append(error_msg)
                        return False, error_msg
                    
                    if not has_message_end:
                        error_msg = f"Round {round_num}: Missing message_end event"
                        self.errors.append(error_msg)
                        return False, error_msg
                    
                    print(f"  Round {round_num}: Received {message_count} chunks, length={len(full_content)}")
                    return True, full_content
                    
        except Exception as e:
            error_msg = f"Round {round_num}: Exception - {str(e)}"
            self.errors.append(error_msg)
            return False, error_msg
    
    async def run_test_round(self, round_num: int) -> bool:
        """执行一轮完整测试"""
        print(f"\n{'='*60}")
        print(f"Test Round {round_num}")
        print(f"{'='*60}")
        
        test_cases = [
            ("我想出差", "Initial request"),
            ("去深圳", "Provide destination"),
            ("我是经理", "Provide level"),
        ]
        
        round_success = True
        
        for i, (message, description) in enumerate(test_cases, 1):
            print(f"\n  Test {i}: {description}")
            print(f"  Sending: {message}")
            
            success, result = await self.test_stream_chat(message, round_num)
            
            if not success:
                round_success = False
                print(f"  {result}")
            else:
                print(f"  Response length: {len(result)} chars")
                if round_num == 1 and i == 1:
                    print(f"  Response preview: {result[:100]}...")
        
        return round_success
    
    async def run_all_tests(self, num_rounds: int = 3) -> bool:
        """执行所有测试轮次"""
        print(f"\n{'='*60}")
        print(f"Integration Tests ({num_rounds} rounds)")
        print(f"{'='*60}")
        print(f"Session ID: {self.session_id}")
        
        successful_rounds = 0
        
        for round_num in range(1, num_rounds + 1):
            success = await self.run_test_round(round_num)
            if success:
                successful_rounds += 1
                print(f"\nRound {round_num} PASSED")
            else:
                print(f"\nRound {round_num} FAILED")
        
        print(f"\n{'='*60}")
        print(f"Results Summary")
        print(f"{'='*60}")
        print(f"Total rounds: {num_rounds}")
        print(f"Passed: {successful_rounds}")
        print(f"Failed: {num_rounds - successful_rounds}")
        
        if self.errors:
            print(f"\nErrors:")
            for error in self.errors:
                print(f"  - {error}")
        
        all_passed = successful_rounds == num_rounds
        if all_passed:
            print(f"\nAll tests PASSED!")
        else:
            print(f"\nSome tests FAILED")
        
        return all_passed


def test_frontend_build():
    """测试前端构建"""
    print(f"\n{'='*60}")
    print("Frontend Build Test")
    print(f"{'='*60}")
    
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd="/workspace",
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("Frontend build PASSED")
        return True
    else:
        print("Frontend build FAILED")
        print(result.stderr[-500:] if len(result.stderr) > 500 else result.stderr)
        return False


async def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("Integration Test System")
    print("="*60)
    
    test = IntegrationTest()
    
    try:
        success = await test.run_all_tests(num_rounds=3)
        frontend_success = test_frontend_build()
        
        if success and frontend_success:
            print("\n" + "="*60)
            print("ALL TESTS PASSED!")
            print("="*60)
            sys.exit(0)
        else:
            print("\n" + "="*60)
            print("SOME TESTS FAILED")
            print("="*60)
            sys.exit(1)
    except Exception as e:
        print(f"\nTest execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
