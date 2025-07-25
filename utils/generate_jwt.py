#!/usr/bin/env python3
"""Simple utility to generate a JWT token for testing.

Usage:
  python utils/generate_jwt.py --username alice --secret mysecret --expire 60

If --secret is omitted, the script uses the SECRET_KEY environment variable or
falls back to the example key from the repository.
"""
import argparse
import os
from datetime import datetime, timedelta

import jwt

DEFAULT_SECRET = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a JWT token")
    parser.add_argument("--username", required=True, help="Username for the token (stored in 'sub')")
    parser.add_argument("--secret", help="Secret key used to sign the token")
    parser.add_argument("--expire", type=int, default=60, help="Expiration time in minutes")
    args = parser.parse_args()

    secret = args.secret or DEFAULT_SECRET
    payload = {
        "sub": args.username,
        "exp": datetime.utcnow() + timedelta(minutes=args.expire),
    }

    token = jwt.encode(payload, secret, algorithm=ALGORITHM)
    print(token)


if __name__ == "__main__":
    main()
