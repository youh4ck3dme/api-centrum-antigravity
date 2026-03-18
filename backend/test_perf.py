import time
import httpx

async def test_performance():
    url = "http://localhost:8888/api/domains/portfolio"
    
    # 1. First run - should take longer as it loads fresh data
    print("--- 1. First Fetch ---")
    start = time.time()
    
    # We must allow gzip compression explicitly in httpx to test it
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Mocking auth token skip for test purposes, assuming backend doesn't strictly block this internal route without it
        # Actually, let's just make a generic call if auth is required, we use the health endpoint for gzip
        health_url = "http://localhost:8888/api/domains"
        try:
            r1 = await client.get(health_url, headers={"Accept-Encoding": "gzip"})
            dur1 = time.time() - start
            print(f"Time: {dur1:.4f}s")
            print(f"Status: {r1.status_code}")
            # Check headers for content-encoding
            print(f"Content-Encoding: {r1.headers.get('content-encoding', 'None')}")
            # Check length to see if it's smaller
            print(f"Data length: {len(r1.content)} bytes")
        except Exception as e:
            print(e)
            
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_performance())
