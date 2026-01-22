#!/usr/bin/env python3
"""Envelope management for DigiSign API."""

import argparse
import json
import sys

from utils import (
    get_access_token, api_request, api_request_binary, paginate,
    print_json, print_error, confirm,
    DigiSignError, ValidationError
)


def cmd_list(args):
    """List envelopes."""
    try:
        token = get_access_token()

        params = {}
        if args.status:
            params["status"] = args.status
        if args.updated_since:
            params["updatedAt[after]"] = args.updated_since

        if args.all:
            envelopes = list(paginate("/api/envelopes", token, params=params, max_pages=args.max_pages))
        else:
            envelopes = api_request("GET", "/api/envelopes", token, params=params)
            if isinstance(envelopes, dict):
                envelopes = envelopes.get("items", envelopes.get("hydra:member", envelopes.get("member", [])))

        print_json(envelopes)

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_get(args):
    """Get envelope details."""
    try:
        token = get_access_token()
        envelope = api_request("GET", f"/api/envelopes/{args.id}", token)
        print_json(envelope)

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_create(args):
    """Create new envelope."""
    try:
        token = get_access_token()

        data = {}
        if args.name:
            data["name"] = args.name
        if args.email_body:
            data["emailBody"] = args.email_body
        if args.email_body_completed:
            data["emailBodyCompleted"] = args.email_body_completed
        if args.sender_name:
            data["senderName"] = args.sender_name
        if args.sender_email:
            data["senderEmail"] = args.sender_email
        if args.expires_at:
            data["expiresAt"] = args.expires_at
        if args.metadata:
            data["metadata"] = json.loads(args.metadata)

        envelope = api_request("POST", "/api/envelopes", token, data=data)
        print_json(envelope)

    except ValidationError as e:
        print_error(f"{e}: {e.violations}")
        sys.exit(1)
    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_update(args):
    """Update envelope."""
    try:
        token = get_access_token()

        data = {}
        if args.name:
            data["name"] = args.name
        if args.email_body:
            data["emailBody"] = args.email_body
        if args.email_body_completed:
            data["emailBodyCompleted"] = args.email_body_completed
        if args.sender_name:
            data["senderName"] = args.sender_name
        if args.sender_email:
            data["senderEmail"] = args.sender_email
        if args.expires_at:
            data["expiresAt"] = args.expires_at
        if args.metadata:
            data["metadata"] = json.loads(args.metadata)

        envelope = api_request("PATCH", f"/api/envelopes/{args.id}", token, data=data)
        print_json(envelope)

    except ValidationError as e:
        print_error(f"{e}: {e.violations}")
        sys.exit(1)
    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_delete(args):
    """Delete envelope."""
    try:
        token = get_access_token()

        if not args.yes:
            if not confirm(f"Delete envelope {args.id}?"):
                print("Cancelled")
                return

        api_request("DELETE", f"/api/envelopes/{args.id}", token, expected_status=[204])
        print(f"Envelope {args.id} deleted")

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_send(args):
    """Send envelope for signing."""
    try:
        token = get_access_token()

        if not args.yes:
            print("WARNING: Sending an envelope will:")
            print("  - Send emails to all recipients")
            print("  - Incur billing charges")
            print()
            if not confirm(f"Send envelope {args.id}?"):
                print("Cancelled")
                return

        result = api_request("POST", f"/api/envelopes/{args.id}/send", token, expected_status=[200, 204])
        if result:
            print_json(result)
        else:
            print(f"Envelope {args.id} sent successfully")

    except ValidationError as e:
        print_error(f"{e}: {e.violations}")
        sys.exit(1)
    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_cancel(args):
    """Cancel sent envelope."""
    try:
        token = get_access_token()

        if not args.yes:
            if not confirm(f"Cancel envelope {args.id}?"):
                print("Cancelled")
                return

        result = api_request("POST", f"/api/envelopes/{args.id}/cancel", token, expected_status=[200, 204])
        if result:
            print_json(result)
        else:
            print(f"Envelope {args.id} cancelled")

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_download(args):
    """Download signed documents."""
    try:
        token = get_access_token()

        params = {}
        if args.output_format:
            params["output"] = args.output_format
        if args.include_log is not None:
            params["include_log"] = str(args.include_log).lower()

        endpoint = f"/api/envelopes/{args.id}/download"
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            endpoint = f"{endpoint}?{query}"

        data = api_request_binary("GET", endpoint, token)

        if args.output:
            with open(args.output, "wb") as f:
                f.write(data)
            print(f"Downloaded to {args.output}")
        else:
            sys.stdout.buffer.write(data)

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_download_url(args):
    """Get download URL for signed documents."""
    try:
        token = get_access_token()

        params = {}
        if args.output_format:
            params["output"] = args.output_format
        if args.include_log is not None:
            params["include_log"] = str(args.include_log).lower()

        result = api_request("GET", f"/api/envelopes/{args.id}/download-url", token, params=params)
        print_json(result)

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="DigiSign envelope management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list command
    list_parser = subparsers.add_parser("list", help="List envelopes")
    list_parser.add_argument("--status", help="Filter by status (draft, sent, completed, expired, declined, cancelled)")
    list_parser.add_argument("--updated-since", help="Filter by updated date (ISO format)")
    list_parser.add_argument("--all", action="store_true", help="Fetch all pages")
    list_parser.add_argument("--max-pages", type=int, help="Maximum pages to fetch")
    list_parser.set_defaults(func=cmd_list)

    # get command
    get_parser = subparsers.add_parser("get", help="Get envelope details")
    get_parser.add_argument("id", help="Envelope ID")
    get_parser.set_defaults(func=cmd_get)

    # create command
    create_parser = subparsers.add_parser("create", help="Create new envelope")
    create_parser.add_argument("--name", help="Envelope name (email subject)")
    create_parser.add_argument("--email-body", help="Email body text (HTML allowed)")
    create_parser.add_argument("--email-body-completed", help="Email body for completion notification")
    create_parser.add_argument("--sender-name", help="Sender display name")
    create_parser.add_argument("--sender-email", help="Sender email address")
    create_parser.add_argument("--expires-at", help="Expiration date (ISO format)")
    create_parser.add_argument("--metadata", help="Custom metadata (JSON object)")
    create_parser.set_defaults(func=cmd_create)

    # update command
    update_parser = subparsers.add_parser("update", help="Update envelope")
    update_parser.add_argument("id", help="Envelope ID")
    update_parser.add_argument("--name", help="Envelope name (email subject)")
    update_parser.add_argument("--email-body", help="Email body text (HTML allowed)")
    update_parser.add_argument("--email-body-completed", help="Email body for completion notification")
    update_parser.add_argument("--sender-name", help="Sender display name")
    update_parser.add_argument("--sender-email", help="Sender email address")
    update_parser.add_argument("--expires-at", help="Expiration date (ISO format)")
    update_parser.add_argument("--metadata", help="Custom metadata (JSON object)")
    update_parser.set_defaults(func=cmd_update)

    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete envelope")
    delete_parser.add_argument("id", help="Envelope ID")
    delete_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    delete_parser.set_defaults(func=cmd_delete)

    # send command
    send_parser = subparsers.add_parser("send", help="Send envelope for signing")
    send_parser.add_argument("id", help="Envelope ID")
    send_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation (CAUTION: incurs charges)")
    send_parser.set_defaults(func=cmd_send)

    # cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel sent envelope")
    cancel_parser.add_argument("id", help="Envelope ID")
    cancel_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    cancel_parser.set_defaults(func=cmd_cancel)

    # download command
    download_parser = subparsers.add_parser("download", help="Download signed documents")
    download_parser.add_argument("id", help="Envelope ID")
    download_parser.add_argument("--output", "-o", help="Output file path")
    download_parser.add_argument("--output-format", choices=["separate", "combined", "only_log"], help="Output format")
    download_parser.add_argument("--include-log", type=bool, help="Include audit log")
    download_parser.set_defaults(func=cmd_download)

    # download-url command
    url_parser = subparsers.add_parser("download-url", help="Get download URL")
    url_parser.add_argument("id", help="Envelope ID")
    url_parser.add_argument("--output-format", choices=["separate", "combined", "only_log"], help="Output format")
    url_parser.add_argument("--include-log", type=bool, help="Include audit log")
    url_parser.set_defaults(func=cmd_download_url)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
