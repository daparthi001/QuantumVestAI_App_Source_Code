#!/usr/bin/env python3
"""
Test script to validate the new API endpoints work correctly
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_endpoints():
    """Test the new endpoints"""
    try:
        # Test importing the routers
        print("Testing router imports...")
        
        from routers.content import router as content_router
        print("✓ Content router imported successfully")
        print(f"  Prefix: {content_router.prefix}")
        print(f"  Routes: {[route.path for route in content_router.routes]}")
        
        from routers.ai_data import router as ai_data_router
        print("✓ AI data router imported successfully")
        print(f"  Prefix: {ai_data_router.prefix}")
        print(f"  Routes: {[route.path for route in ai_data_router.routes]}")
        
        # Test calling the content endpoints
        print("\nTesting content endpoints...")
        
        # Test news endpoint
        news = await content_router.routes[0].endpoint()
        print(f"✓ News endpoint returns {len(news)} articles")
        
        # Test trending endpoint  
        trending = await content_router.routes[1].endpoint()
        print(f"✓ Trending endpoint returns {len(trending)} topics")
        
        # Test market movers endpoint
        movers = await content_router.routes[2].endpoint()
        print(f"✓ Market movers endpoint returns {len(movers)} symbols")
        
        # Test AI recommendations endpoint
        recommendations = await content_router.routes[3].endpoint()
        print(f"✓ AI recommendations endpoint returns {len(recommendations)} items")
        
        print("\n✅ All endpoint tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_endpoints())
    sys.exit(0 if success else 1)