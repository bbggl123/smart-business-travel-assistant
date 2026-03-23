import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


async def test_agents():
    print("=" * 50)
    print("Agent System Tests")
    print("=" * 50)

    from app.agents import (
        DispatcherAgent,
        IntentUnderstandingAgent,
        TransportationAgent,
        HotelAgent,
        DiningAgent,
        ComplianceAgent
    )

    dispatcher = DispatcherAgent()
    intent_agent = IntentUnderstandingAgent()
    transport_agent = TransportationAgent()
    hotel_agent = HotelAgent()
    dining_agent = DiningAgent()
    compliance_agent = ComplianceAgent()

    print("\n=== Test 1: Dispatcher Agent ===")
    result = await dispatcher.process({
        "session_id": "test_session",
        "intent_type": "trip_planning"
    })
    print(f"Workflow created: {result.get('workflow_id')}")
    print(f"Tasks: {len(result.get('tasks', []))}")
    assert result["status"] == "created"
    print("✅ Dispatcher Agent PASSED\n")

    print("\n=== Test 2: Intent Understanding Agent ===")
    result = await intent_agent.process({
        "session_id": "test_session",
        "message": "我要去上海出差，3月25号出发，27号回来"
    })
    print(f"Intent type: {result.get('intent_type')}")
    print(f"Entities: {result.get('entities')}")
    print(f"Missing fields: {result.get('missing_fields')}")
    assert result["status"] == "completed"
    print("✅ Intent Agent PASSED\n")

    print("\n=== Test 3: Transportation Agent ===")
    result = await transport_agent.process({
        "action": "search",
        "departure": "北京",
        "destination": "上海",
        "date": "2026-04-01"
    })
    print(f"Found {result.get('count', 0)} transport options")
    assert result["status"] == "completed"
    print("✅ Transportation Agent PASSED\n")

    print("\n=== Test 4: Hotel Agent ===")
    result = await hotel_agent.process({
        "action": "search",
        "city": "上海",
        "check_in": "2026-04-01",
        "check_out": "2026-04-03",
        "user_level": "经理级"
    })
    print(f"Compliant hotels: {result.get('total_compliant')}")
    print(f"Alternative hotels: {result.get('total_alternative')}")
    assert result["status"] == "completed"
    print("✅ Hotel Agent PASSED\n")

    print("\n=== Test 5: Dining Agent ===")
    result = await dining_agent.process({
        "action": "search",
        "city": "上海",
        "date": "2026-04-01",
        "headcount": 3
    })
    print(f"Compliant restaurants: {result.get('total_compliant')}")
    print(f"Over budget restaurants: {result.get('total_over_budget')}")
    assert result["status"] == "completed"
    print("✅ Dining Agent PASSED\n")

    print("\n=== Test 6: Compliance Agent ===")
    result = await compliance_agent.process({
        "action": "check",
        "category": "hotel",
        "user_level": "经理级",
        "city": "上海",
        "amount": 600.0
    })
    print(f"Compliance check: {result}")
    assert result["is_compliant"] == True
    print("✅ Compliance Agent PASSED\n")

    print("\n=== Test 7: Compliance Agent - Over Budget ===")
    result = await compliance_agent.process({
        "action": "check",
        "category": "hotel",
        "user_level": "基层员工",
        "city": "北京",
        "amount": 500.0
    })
    print(f"Compliance check: {result}")
    assert result["is_compliant"] == False
    assert result["over_budget"] == 100.0
    print("✅ Compliance Agent (Over Budget) PASSED\n")

    print("=" * 50)
    print("ALL AGENT TESTS PASSED ✅")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_agents())
