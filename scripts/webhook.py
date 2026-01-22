#!/usr/bin/env python3
"""Webhook management for DigiSign API."""

import argparse
import hashlib
import hmac
import json
import sys
import time

from utils import (
    get_access_token, api_request, paginate,
    print_json, print_error, confirm,
    DigiSignError, ValidationError
)


EVENTS = [
    "envelopeSent", "envelopeCompleted", "envelopeExpired", "envelopeDeclined",
    "envelopeDisapproved", "envelopeCancelled", "envelopeDeleted",
    "recipientSent", "recipientDelivered", "recipientNonDelivered",
    "recipientAuthFailed", "recipientSigned", "recipientDownloaded",
    "recipientDeclined", "recipientDisapproved", "recipientCanceled"
]
STATUSES = ["enabled", "paused"]


def cmd_list(args):
    """List webhooks."""
    try:
        token = get_access_token()

        if args.all:
            webhooks = list(paginate("/api/webhooks", token, max_pages=args.max_pages))
        else:
            result = api_request("GET", "/api/webhooks", token)
            webhooks = result if isinstance(result, list) else result.get("items", result.get("hydra:member", result.get("member", [])))

        print_json(webhooks)

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_create(args):
    """Create webhook."""
    try:
        token = get_access_token()

        data = {
            "event": args.event,
            "url": args.url,
        }

        if args.status:
            data["status"] = args.status

        # OAuth 2.0 security (optional)
        if args.oauth_token_endpoint:
            data["oAuthTokenEndpoint"] = args.oauth_token_endpoint
        if args.oauth_client_id:
            data["oAuthClientId"] = args.oauth_client_id
        if args.oauth_client_secret:
            data["oAuthClientSecret"] = args.oauth_client_secret
        if args.oauth_scopes:
            data["oAuthScopes"] = [s.strip() for s in args.oauth_scopes.split(",")]

        result = api_request("POST", "/api/webhooks", token, data=data)
        print_json(result)

    except ValidationError as e:
        print_error(f"{e}: {e.violations}")
        sys.exit(1)
    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_get(args):
    """Get webhook details."""
    try:
        token = get_access_token()
        result = api_request("GET", f"/api/webhooks/{args.id}", token)
        print_json(result)

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_update(args):
    """Update webhook."""
    try:
        token = get_access_token()

        data = {}
        if args.url:
            data["url"] = args.url
        if args.status:
            data["status"] = args.status
        if args.oauth_token_endpoint:
            data["oAuthTokenEndpoint"] = args.oauth_token_endpoint
        if args.oauth_client_id:
            data["oAuthClientId"] = args.oauth_client_id
        if args.oauth_client_secret:
            data["oAuthClientSecret"] = args.oauth_client_secret
        if args.oauth_scopes:
            data["oAuthScopes"] = [s.strip() for s in args.oauth_scopes.split(",")]

        result = api_request("PUT", f"/api/webhooks/{args.id}", token, data=data)
        print_json(result)

    except ValidationError as e:
        print_error(f"{e}: {e.violations}")
        sys.exit(1)
    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_delete(args):
    """Delete webhook."""
    try:
        token = get_access_token()

        if not args.yes:
            if not confirm(f"Delete webhook {args.id}?"):
                print("Cancelled")
                return

        api_request("DELETE", f"/api/webhooks/{args.id}", token, expected_status=[204])
        print(f"Webhook {args.id} deleted")

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_test(args):
    """Test webhook (send test event)."""
    try:
        token = get_access_token()
        result = api_request(
            "POST",
            f"/api/webhooks/{args.id}/test",
            token,
            expected_status=[200, 204]
        )
        if result:
            print_json(result)
        else:
            print(f"Test event sent to webhook {args.id}")

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_attempts(args):
    """List webhook delivery attempts."""
    try:
        token = get_access_token()
        result = api_request("GET", f"/api/webhooks/{args.id}/attempts", token)

        attempts = result if isinstance(result, list) else result.get("items", result.get("hydra:member", result.get("member", [])))
        print_json(attempts)

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_resend(args):
    """Resend failed webhook attempt."""
    try:
        token = get_access_token()
        result = api_request(
            "POST",
            f"/api/webhooks/{args.webhook_id}/attempts/{args.attempt_id}/resend",
            token,
            expected_status=[200, 204]
        )
        if result:
            print_json(result)
        else:
            print(f"Attempt {args.attempt_id} resent")

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_verify_signature(args):
    """Verify webhook signature (for testing/debugging)."""
    # Parse signature header: t=timestamp,s=signature
    header = args.signature
    parts = dict(p.split("=", 1) for p in header.split(","))

    timestamp = int(parts.get("t", 0))
    signature = parts.get("s", "")

    # Check timestamp age
    age = time.time() - timestamp
    if age > 300:  # 5 minutes
        print_error(f"Timestamp too old: {age:.0f} seconds")
        sys.exit(1)

    # Calculate expected signature
    payload = f"{timestamp}.{args.body}"
    expected = hmac.new(
        args.secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    if hmac.compare_digest(expected, signature):
        print("Signature valid")
    else:
        print_error("Signature invalid")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="DigiSign webhook management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list command
    list_parser = subparsers.add_parser("list", help="List webhooks")
    list_parser.add_argument("--all", action="store_true", help="Fetch all pages")
    list_parser.add_argument("--max-pages", type=int, help="Maximum pages to fetch")
    list_parser.set_defaults(func=cmd_list)

    # create command
    create_parser = subparsers.add_parser("create", help="Create webhook")
    create_parser.add_argument("--event", required=True, choices=EVENTS, help="Event to subscribe to")
    create_parser.add_argument("--url", required=True, help="Webhook URL")
    create_parser.add_argument("--status", choices=STATUSES, default="enabled", help="Initial status")
    create_parser.add_argument("--oauth-token-endpoint", help="OAuth token endpoint")
    create_parser.add_argument("--oauth-client-id", help="OAuth client ID")
    create_parser.add_argument("--oauth-client-secret", help="OAuth client secret")
    create_parser.add_argument("--oauth-scopes", help="OAuth scopes (comma-separated)")
    create_parser.set_defaults(func=cmd_create)

    # get command
    get_parser = subparsers.add_parser("get", help="Get webhook details")
    get_parser.add_argument("id", help="Webhook ID")
    get_parser.set_defaults(func=cmd_get)

    # update command
    update_parser = subparsers.add_parser("update", help="Update webhook")
    update_parser.add_argument("id", help="Webhook ID")
    update_parser.add_argument("--url", help="Webhook URL")
    update_parser.add_argument("--status", choices=STATUSES, help="Status")
    update_parser.add_argument("--oauth-token-endpoint", help="OAuth token endpoint")
    update_parser.add_argument("--oauth-client-id", help="OAuth client ID")
    update_parser.add_argument("--oauth-client-secret", help="OAuth client secret")
    update_parser.add_argument("--oauth-scopes", help="OAuth scopes (comma-separated)")
    update_parser.set_defaults(func=cmd_update)

    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete webhook")
    delete_parser.add_argument("id", help="Webhook ID")
    delete_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    delete_parser.set_defaults(func=cmd_delete)

    # test command
    test_parser = subparsers.add_parser("test", help="Send test event to webhook")
    test_parser.add_argument("id", help="Webhook ID")
    test_parser.set_defaults(func=cmd_test)

    # attempts command
    attempts_parser = subparsers.add_parser("attempts", help="List delivery attempts")
    attempts_parser.add_argument("id", help="Webhook ID")
    attempts_parser.set_defaults(func=cmd_attempts)

    # resend command
    resend_parser = subparsers.add_parser("resend", help="Resend failed attempt")
    resend_parser.add_argument("webhook_id", help="Webhook ID")
    resend_parser.add_argument("attempt_id", help="Attempt ID")
    resend_parser.set_defaults(func=cmd_resend)

    # verify-signature command
    verify_parser = subparsers.add_parser("verify-signature", help="Verify webhook signature")
    verify_parser.add_argument("--signature", required=True, help="Signature header value (t=...,s=...)")
    verify_parser.add_argument("--body", required=True, help="Request body")
    verify_parser.add_argument("--secret", required=True, help="Webhook secret")
    verify_parser.set_defaults(func=cmd_verify_signature)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
