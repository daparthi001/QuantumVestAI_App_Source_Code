#!/usr/bin/env python3
"""
Test Market Data Endpoint for QuantumVestAI
Created: 2025-08-04
"""
import argparse
import asyncio
import json
import logging
import sys

import httpx

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("market_data_tester")


async def test_endpoint(
    base_url="http://localhost:3000", symbol="SPY", timeout=10, use_curl=False
):
    """Test the market data endpoint"""
    endpoint = f"{base_url}/api/ai/market-data/{symbol}"
    logger.info(f"Testing endpoint: {endpoint}")
    
    if use_curl:
        import subprocess
        
        logger.info("Using curl to test endpoint")
        result = subprocess.run(
            ["curl", "-s", endpoint], capture_output=True, text=True, check=False
        )
        logger.info(f"Curl exit code: {result.returncode}")
        
        if result.returncode != 0:
            logger.error(f"Curl error: {result.stderr}")
            return False
            
        try:
            data = json.loads(result.stdout)
            logger.info(f"Got response with keys: {list(data.keys())}")
            
            if "timestamps" in data and "prices" in data:
                logger.info(
                    f"Success! Got {len(data['timestamps'])} timestamps and {len(data['prices'])} prices"
                )
                return True
            else:
                logger.error(f"Missing expected data keys. Response: {data}")
                return False
        except json.JSONDecodeError:
            logger.error("Invalid JSON response")
            logger.error(f"Response: {result.stdout[:1000]}")
            return False
    
    else:
        try:
            logger.info("Using httpx to test endpoint")
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(endpoint)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Got response with keys: {list(data.keys())}")
                
                if "timestamps" in data and "prices" in data:
                    logger.info(
                        f"Success! Got {len(data['timestamps'])} timestamps and {len(data['prices'])} prices"
                    )
                    return True
                else:
                    logger.error(f"Missing expected data keys. Response: {data}")
                    return False
        except httpx.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error: {e}")
            return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the market data endpoint")
    parser.add_argument(
        "--url", default="http://localhost:3000", help="Base URL of the API"
    )
    parser.add_argument("--symbol", default="SPY", help="Symbol to test with")
    parser.add_argument(
        "--timeout", type=int, default=10, help="Request timeout in seconds"
    )
    parser.add_argument(
        "--curl", action="store_true", help="Use curl instead of httpx"
    )
    
    args = parser.parse_args()
    
    success = asyncio.run(
        test_endpoint(args.url, args.symbol, args.timeout, args.curl)
    )
    
    if success:
        logger.info("✅ Test passed!")
        sys.exit(0)
    else:
        logger.error("❌ Test failed!")
        sys.exit(1)
