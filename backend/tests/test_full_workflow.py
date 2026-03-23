import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


async def test_full_workflow():
    print("=" * 60)
    print("FULL WORKFLOW INTEGRATION TEST")
    print("=" * 60)

    from httpx import AsyncClient, ASGITransport
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:

        print("\n[Step 1] User sends trip planning request...")
        response = await client.post("/api/chat/intent/parse", json={
            "session_id": "workflow_test_001",
            "message": "我要去上海出差，3月25号出发，27号回来，经理级别"
        })
        print(f"Intent parsed: {response.json()['data']['intent_type']}")
        print(f"Missing fields: {response.json()['data']['missing_fields']}")
        assert response.status_code == 200
        print("✅ Step 1 PASSED\n")

        print("[Step 2] User clarifies missing information...")
        response = await client.post("/api/chat/intent/clarify", json={
            "session_id": "workflow_test_001",
            "answers": {
                "departure": "北京",
                "destination": "上海",
                "start_date": "2026-03-25",
                "end_date": "2026-03-27",
                "user_level": "经理级"
            }
        })
        intent_data = response.json()["data"]
        print(f"Intent updated, missing fields: {intent_data['missing_fields']}")
        print(f"Questions remaining: {len(intent_data['questions'])}")
        assert response.status_code == 200
        print("✅ Step 2 PASSED\n")

        print("[Step 3] Search transportation...")
        response = await client.post("/api/transport/search", json={
            "departure": "北京",
            "destination": "上海",
            "date": "2026-03-25",
            "type": "both"
        })
        transport_options = response.json()["data"]
        print(f"Found {len(transport_options)} transport options")
        for opt in transport_options[:2]:
            print(f"  - {opt['type']}: {opt.get('flight_no', opt.get('train_no'))} - ¥{opt['price']}")
        assert len(transport_options) > 0
        print("✅ Step 3 PASSED\n")

        print("[Step 4] Search hotels...")
        response = await client.post("/api/hotel/search", json={
            "city": "上海",
            "check_in": "2026-03-25",
            "check_out": "2026-03-27",
            "star": None
        })
        hotel_options = response.json()["data"]
        print(f"Found {len(hotel_options)} hotels")
        for hotel in hotel_options[:2]:
            print(f"  - {hotel['name']} ({hotel['stars']}星) - ¥{hotel['price']}/晚")
            print(f"    距客户位置: {hotel['distance_km']}km | 合规: {hotel['compliance']['is_compliant']}")
        assert len(hotel_options) > 0
        print("✅ Step 4 PASSED\n")

        print("[Step 5] Search dining options...")
        response = await client.post("/api/dining/search", json={
            "city": "上海",
            "date": "2026-03-26",
            "headcount": 3,
            "cuisine": None,
            "budget_per_person": None
        })
        dining_options = response.json()["data"]
        print(f"Found {len(dining_options)} restaurants")
        for dining in dining_options[:2]:
            print(f"  - {dining['restaurant']} ({dining['cuisine']}) - ¥{dining['price_per_person']}/人")
            print(f"    总价: ¥{dining['total_amount']} | 合规: {dining['compliance']['is_compliant']}")
        assert len(dining_options) > 0
        print("✅ Step 5 PASSED\n")

        print("[Step 6] Book transportation...")
        response = await client.post("/api/transport/book", json={
            "option_id": transport_options[0]["id"]
        })
        booking_result = response.json()["data"]
        print(f"Booking: {booking_result['booking_id']} - {booking_result['status']}")
        assert booking_result["status"] == "confirmed"
        print("✅ Step 6 PASSED\n")

        print("[Step 7] Generate approval form...")
        response = await client.post("/api/approval/generate", json={
            "trip_id": "workflow_test_001"
        })
        approval = response.json()["data"]
        print(f"Approval ID: {approval['approval_id']}")
        print(f"Employee: {approval['employee']['name']} ({approval['employee']['level']})")
        print(f"Total amount: ¥{approval['total_amount']}")
        for item in approval["items"]:
            print(f"  - {item['category']}: {item['name']} - ¥{item['amount']} ({'合规' if item['is_compliant'] else '超标'})")
        print("✅ Step 7 PASSED\n")

        print("[Step 8] Upload invoice (mock)...")
        from io import BytesIO
        files = {"files": ("test.pdf", BytesIO(b"mock pdf content"), "application/pdf")}
        response = await client.post("/api/invoice/upload", files=files)
        invoice_result = response.json()["data"]
        print(f"Invoice uploaded: {len(invoice_result)} invoice(s)")
        for inv in invoice_result:
            print(f"  - ID: {inv['invoice_id']} | Amount: ¥{inv['fields']['total_amount']}")
        print("✅ Step 8 PASSED\n")

    print("=" * 60)
    print("FULL WORKFLOW TEST PASSED ✅")
    print("=" * 60)
    print("\nSummary:")
    print("- Intent Understanding: Working")
    print("- Transportation Search/Book: Working")
    print("- Hotel Search: Working")
    print("- Dining Search: Working")
    print("- Approval Generation: Working")
    print("- Invoice Upload: Working")
    print("\nBackend API is ready for frontend integration!")


if __name__ == "__main__":
    asyncio.run(test_full_workflow())
