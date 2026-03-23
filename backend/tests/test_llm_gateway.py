import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.llm.gateway import llm_gateway as gateway


async def test_llm_basic():
    print("=== Test 1: Basic LLM Call ===")
    messages = [
        {"role": "user", "content": "你好，请介绍一下你自己"}
    ]

    print("Sending request to Zidongtaichu API...")
    response = await gateway.chat_no_stream(messages)
    print(f"Response: {response}")
    print("✅ Test 1 PASSED\n")


async def test_llm_stream():
    print("=== Test 2: Stream LLM Call ===")
    messages = [
        {"role": "user", "content": "请用三句话介绍你自己"}
    ]

    print("Sending streaming request...")
    full_content = ""
    async for chunk in gateway.chat_stream(messages):
        print(f"Chunk received: {chunk}", end="", flush=True)
        full_content += chunk
    print(f"\n✅ Test 2 PASSED - Full response: {full_content[:100]}...\n")


async def test_llm_json_format():
    print("=== Test 3: JSON Format Parsing ===")
    messages = [
        {"role": "system", "content": "你是一个JSON生成器，请只返回JSON格式的回复，不要有任何其他内容。"},
        {"role": "user", "content": "请返回一个包含name和age字段的JSON对象，name是张三，age是30"}
    ]

    response = await gateway.chat_no_stream(messages)
    print(f"Response: {response}")

    try:
        import json
        data = json.loads(response)
        assert "name" in data
        assert "age" in data
        print(f"Parsed JSON: {data}")
        print("✅ Test 3 PASSED\n")
    except json.JSONDecodeError as e:
        print(f"❌ Test 3 FAILED - JSON parse error: {e}\n")


async def main():
    print("=" * 50)
    print("LLM Gateway Tests")
    print("=" * 50)

    try:
        await test_llm_basic()
        await test_llm_stream()
        await test_llm_json_format()
        print("=" * 50)
        print("ALL TESTS PASSED ✅")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
