import asyncio
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


async def test_api_endpoints():
    print("=" * 50)
    print("API Endpoints Tests")
    print("=" * 50)

    from httpx import AsyncClient, ASGITransport
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:

        print("\n=== Test: Health Check ===")
        response = await client.get("/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        assert response.status_code == 200
        print("✅ Health Check PASSED\n")

        print("\n=== Test: Intent Parse ===")
        response = await client.post("/api/chat/intent/parse", json={
            "session_id": "test_session",
            "message": "我要去上海出差，3月25号出发，27号回来"
        })
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, ensure_ascii=False)[:500]}")
        assert response.status_code == 200
        assert result["code"] == 0
        print("✅ Intent Parse PASSED\n")

        print("\n=== Test: Transport Search ===")
        response = await client.post("/api/transport/search", json={
            "departure": "北京",
            "destination": "上海",
            "date": "2026-04-01",
            "type": "both"
        })
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Found {len(result.get('data', []))} options")
        assert response.status_code == 200
        assert result["code"] == 0
        print("✅ Transport Search PASSED\n")

        print("\n=== Test: Hotel Search ===")
        response = await client.post("/api/hotel/search", json={
            "city": "上海",
            "check_in": "2026-04-01",
            "check_out": "2026-04-03",
            "star": None
        })
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Found {len(result.get('data', []))} hotels")
        assert response.status_code == 200
        assert result["code"] == 0
        print("✅ Hotel Search PASSED\n")

        print("\n=== Test: Dining Search ===")
        response = await client.post("/api/dining/search", json={
            "city": "上海",
            "date": "2026-04-01",
            "headcount": 3,
            "cuisine": None,
            "budget_per_person": None
        })
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Found {len(result.get('data', []))} restaurants")
        assert response.status_code == 200
        assert result["code"] == 0
        print("✅ Dining Search PASSED\n")

        print("\n=== Test: Approval Generate ===")
        response = await client.post("/api/approval/generate", json={
            "trip_id": "test_trip_001"
        })
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Approval ID: {result.get('data', {}).get('approval_id')}")
        assert response.status_code == 200
        assert result["code"] == 0
        print("✅ Approval Generate PASSED\n")

        print("\n=== Test: Transport Book ===")
        response = await client.post("/api/transport/book", json={
            "option_id": "train_001"
        })
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Booking: {result.get('data')}")
        assert response.status_code == 200
        assert result["code"] == 0
        print("✅ Transport Book PASSED\n")

    print("=" * 50)
    print("ALL API TESTS PASSED ✅")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_api_endpoints())
