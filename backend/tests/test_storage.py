import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.storage.supabase import get_supabase
from app.utils.logger import logger


async def test_supabase_connection():
    print("=== Test: Supabase Connection ===")
    try:
        supabase = get_supabase()
        print(f"Connected to Supabase: {supabase}")
        print("✅ Supabase connection successful\n")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_redis_connection():
    print("=== Test: Redis Connection ===")
    try:
        from app.storage.redis_client import get_redis
        redis = await get_redis()
        await redis.ping()
        print(f"Connected to Redis: {redis}")
        print("✅ Redis connection successful\n")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("=" * 50)
    print("Storage Connection Tests")
    print("=" * 50)

    results = []
    results.append(await test_supabase_connection())
    results.append(await test_redis_connection())

    print("=" * 50)
    if all(results):
        print("ALL STORAGE TESTS PASSED ✅")
    else:
        print("SOME STORAGE TESTS FAILED ❌")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
