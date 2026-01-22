#!/usr/bin/env python3
"""Token management for DigiSign API."""

import argparse
import json
import sys
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from utils import (
    get_config, save_token, load_token, print_json, print_error,
    AuthenticationError
)


def get_token(access_key: str, secret_key: str, base_url: str = None) -> dict:
    """Exchange accessKey/secretKey for JWT token.

    Args:
        access_key: API access key
        secret_key: API secret key
        base_url: API base URL

    Returns:
        dict with token, exp, iat
    """
    if base_url is None:
        base_url = get_config()["base_url"]

    url = f"{base_url}/api/auth-token"

    headers = {
        "Content-Type": "application/json",
    }

    data = json.dumps({
        "accessKey": access_key,
        "secretKey": secret_key,
    }).encode("utf-8")

    req = Request(url, data=data, headers=headers, method="POST")

    try:
        with urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        try:
            error_data = json.loads(e.read().decode("utf-8"))
            raise AuthenticationError(
                error_data.get("detail", f"Authentication failed: {e.code}")
            )
        except json.JSONDecodeError:
            raise AuthenticationError(f"Authentication failed: {e.code}")


def cmd_get_token(args):
    """Get new JWT token."""
    config = get_config()

    access_key = config["access_key"]
    secret_key = config["secret_key"]

    if not access_key or not secret_key:
        print_error("DIGISIGN_ACCESS_KEY and DIGISIGN_SECRET_KEY must be set")
        sys.exit(1)

    try:
        token_data = get_token(access_key, secret_key, config["base_url"])

        if args.save:
            save_token(token_data, config["token_file"])
            print(f"Token saved to {config['token_file']}")
            print(f"Expires at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(token_data['exp']))}")
        else:
            print_json(token_data)

    except AuthenticationError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_status(args):
    """Check token status."""
    config = get_config()

    try:
        token_data = load_token(config["token_file"])

        exp = token_data.get("exp", 0)
        iat = token_data.get("iat", 0)
        remaining = exp - time.time()

        status = {
            "token_file": str(config["token_file"]),
            "has_token": bool(token_data.get("token")),
            "issued_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(iat)) if iat else None,
            "expires_at": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(exp)) if exp else None,
            "expires_in_seconds": max(0, int(remaining)),
            "expired": remaining <= 0,
            "api_url": config["base_url"],
        }

        print_json(status)

    except FileNotFoundError:
        print_json({
            "token_file": str(config["token_file"]),
            "exists": False,
            "api_url": config["base_url"],
        })
    except Exception as e:
        print_error(str(e))
        sys.exit(1)


def cmd_clear(args):
    """Clear saved token."""
    config = get_config()
    token_file = config["token_file"]

    if token_file.exists():
        token_file.unlink()
        print(f"Token file removed: {token_file}")
    else:
        print(f"No token file found at: {token_file}")


def main():
    parser = argparse.ArgumentParser(description="DigiSign token management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # get-token command
    token_parser = subparsers.add_parser("get-token", help="Get new JWT token")
    token_parser.add_argument("--save", action="store_true", help="Save token to file")
    token_parser.set_defaults(func=cmd_get_token)

    # status command
    status_parser = subparsers.add_parser("status", help="Check token status")
    status_parser.set_defaults(func=cmd_status)

    # clear command
    clear_parser = subparsers.add_parser("clear", help="Clear saved token")
    clear_parser.set_defaults(func=cmd_clear)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
