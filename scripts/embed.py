#!/usr/bin/env python3
"""Embedding operations for DigiSign API."""

import argparse
import sys

from utils import (
    get_access_token, api_request,
    print_json, print_error,
    DigiSignError, ValidationError
)


def cmd_envelope(args):
    """Get embed URL for envelope editing/sending."""
    try:
        token = get_access_token()

        data = {}
        if args.target:
            data["target"] = args.target
        if args.allowed_actions:
            data["allowedActions"] = [a.strip() for a in args.allowed_actions.split(",")]
        if args.language:
            data["language"] = args.language
        if args.return_url:
            data["returnUrl"] = args.return_url
        if args.expire_at:
            data["expireAt"] = args.expire_at

        result = api_request(
            "POST",
            f"/api/envelopes/{args.envelope_id}/embed",
            token,
            data=data if data else None
        )
        print_json(result)

    except ValidationError as e:
        print_error(f"{e}: {e.violations}")
        sys.exit(1)
    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_recipient(args):
    """Get embed URL for recipient signing session."""
    try:
        token = get_access_token()

        data = {}
        if args.return_url:
            data["returnUrl"] = args.return_url
        if args.failure_url:
            data["failureUrl"] = args.failure_url
        if args.expire_at:
            data["expireAt"] = args.expire_at

        result = api_request(
            "POST",
            f"/api/envelopes/{args.envelope_id}/recipients/{args.recipient_id}/embed",
            token,
            data=data if data else None
        )
        print_json(result)

    except ValidationError as e:
        print_error(f"{e}: {e.violations}")
        sys.exit(1)
    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_signing(args):
    """Get embed URL for signing ceremony (multiple recipients)."""
    try:
        token = get_access_token()

        # Build recipient IRIs
        recipients = []
        for r in args.recipients.split(","):
            r = r.strip()
            if not r.startswith("/api/"):
                r = f"/api/envelopes/{args.envelope_id}/recipients/{r}"
            recipients.append(r)

        data = {
            "recipients": recipients,
        }

        if args.return_url:
            data["returnUrl"] = args.return_url
        if args.expire_at:
            data["expireAt"] = args.expire_at

        result = api_request(
            "POST",
            f"/api/envelopes/{args.envelope_id}/embed/signing",
            token,
            data=data
        )
        print_json(result)

    except ValidationError as e:
        print_error(f"{e}: {e.violations}")
        sys.exit(1)
    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_detail(args):
    """Get embed URL for envelope detail view."""
    try:
        token = get_access_token()

        data = {}
        if args.return_url:
            data["returnUrl"] = args.return_url
        if args.expire_at:
            data["expireAt"] = args.expire_at

        result = api_request(
            "POST",
            f"/api/envelopes/{args.envelope_id}/embed/detail",
            token,
            data=data if data else None
        )
        print_json(result)

    except ValidationError as e:
        print_error(f"{e}: {e.violations}")
        sys.exit(1)
    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="DigiSign embedding operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # envelope command
    env_parser = subparsers.add_parser("envelope", help="Get embed URL for envelope editing")
    env_parser.add_argument("envelope_id", help="Envelope ID")
    env_parser.add_argument("--target", choices=["editor", "send"], help="Embed target")
    env_parser.add_argument("--allowed-actions", help="Comma-separated allowed actions")
    env_parser.add_argument("--language", help="UI language (cs, en, sk, pl)")
    env_parser.add_argument("--return-url", help="URL to redirect after completion")
    env_parser.add_argument("--expire-at", help="URL expiration (ISO datetime)")
    env_parser.set_defaults(func=cmd_envelope)

    # recipient command
    rec_parser = subparsers.add_parser("recipient", help="Get embed URL for recipient signing")
    rec_parser.add_argument("envelope_id", help="Envelope ID")
    rec_parser.add_argument("recipient_id", help="Recipient ID")
    rec_parser.add_argument("--return-url", help="URL to redirect after signing")
    rec_parser.add_argument("--failure-url", help="URL to redirect on error")
    rec_parser.add_argument("--expire-at", help="URL expiration (ISO datetime)")
    rec_parser.set_defaults(func=cmd_recipient)

    # signing command
    sign_parser = subparsers.add_parser("signing", help="Get embed URL for signing ceremony")
    sign_parser.add_argument("envelope_id", help="Envelope ID")
    sign_parser.add_argument("--recipients", required=True, help="Comma-separated recipient IDs")
    sign_parser.add_argument("--return-url", help="URL to redirect after completion")
    sign_parser.add_argument("--expire-at", help="URL expiration (ISO datetime)")
    sign_parser.set_defaults(func=cmd_signing)

    # detail command
    detail_parser = subparsers.add_parser("detail", help="Get embed URL for envelope detail view")
    detail_parser.add_argument("envelope_id", help="Envelope ID")
    detail_parser.add_argument("--return-url", help="URL to redirect on close")
    detail_parser.add_argument("--expire-at", help="URL expiration (ISO datetime)")
    detail_parser.set_defaults(func=cmd_detail)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
