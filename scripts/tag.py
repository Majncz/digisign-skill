#!/usr/bin/env python3
"""Signature tag management for DigiSign API."""

import argparse
import json
import sys

from utils import (
    get_access_token, api_request,
    print_json, print_error, confirm,
    DigiSignError, ValidationError
)


TAG_TYPES = ["signature", "approval", "text", "document", "attachment", "checkbox", "radio_button", "date_of_signature"]
POSITIONING = ["top_left", "top_center", "top_right", "middle_left", "center", "middle_right", "bottom_left", "bottom_center", "bottom_right"]


def cmd_list(args):
    """List tags in envelope."""
    try:
        token = get_access_token()
        result = api_request("GET", f"/api/envelopes/{args.envelope_id}/tags", token)

        tags = result if isinstance(result, list) else result.get("items", result.get("hydra:member", result.get("member", [])))
        print_json(tags)

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_add(args):
    """Add tag to envelope."""
    try:
        token = get_access_token()

        # Build document IRI
        document_iri = args.document
        if not document_iri.startswith("/api/"):
            document_iri = f"/api/envelopes/{args.envelope_id}/documents/{args.document}"

        # Build recipient IRI
        recipient_iri = args.recipient
        if not recipient_iri.startswith("/api/"):
            recipient_iri = f"/api/envelopes/{args.envelope_id}/recipients/{args.recipient}"

        data = {
            "document": document_iri,
            "recipient": recipient_iri,
            "type": args.type,
        }

        # Either use placeholder or coordinates
        if args.placeholder:
            data["placeholder"] = args.placeholder
            if args.positioning:
                data["positioning"] = args.positioning
        else:
            if args.page is None or args.x is None or args.y is None:
                print_error("Either --placeholder or --page/--x/--y coordinates are required")
                sys.exit(1)
            data["page"] = args.page
            data["xPosition"] = args.x
            data["yPosition"] = args.y

        # Optional parameters
        if args.width:
            data["width"] = args.width
        if args.height:
            data["height"] = args.height
        if args.required is not None:
            data["required"] = args.required
        if args.label:
            data["label"] = args.label
        if args.group:
            data["group"] = args.group

        result = api_request(
            "POST",
            f"/api/envelopes/{args.envelope_id}/tags",
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


def cmd_add_by_placeholder(args):
    """Add tags to all placeholder occurrences."""
    try:
        token = get_access_token()

        # Build recipient IRI
        recipient_iri = args.recipient
        if not recipient_iri.startswith("/api/"):
            recipient_iri = f"/api/envelopes/{args.envelope_id}/recipients/{args.recipient}"

        data = {
            "recipient": recipient_iri,
            "type": args.type,
            "placeholder": args.placeholder,
        }

        if args.positioning:
            data["positioning"] = args.positioning
        if args.documents:
            # Convert document IDs to list
            doc_ids = [d.strip() for d in args.documents.split(",")]
            data["applyToDocuments"] = doc_ids
        if args.width:
            data["width"] = args.width
        if args.height:
            data["height"] = args.height
        if args.required is not None:
            data["required"] = args.required
        if args.label:
            data["label"] = args.label

        result = api_request(
            "POST",
            f"/api/envelopes/{args.envelope_id}/tags/by-placeholder",
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


def cmd_get(args):
    """Get tag details."""
    try:
        token = get_access_token()
        result = api_request(
            "GET",
            f"/api/envelopes/{args.envelope_id}/tags/{args.tag_id}",
            token
        )
        print_json(result)

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_update(args):
    """Update tag."""
    try:
        token = get_access_token()

        data = {}
        if args.page is not None:
            data["page"] = args.page
        if args.x is not None:
            data["xPosition"] = args.x
        if args.y is not None:
            data["yPosition"] = args.y
        if args.width:
            data["width"] = args.width
        if args.height:
            data["height"] = args.height
        if args.required is not None:
            data["required"] = args.required
        if args.label:
            data["label"] = args.label

        result = api_request(
            "PUT",
            f"/api/envelopes/{args.envelope_id}/tags/{args.tag_id}",
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


def cmd_delete(args):
    """Delete tag."""
    try:
        token = get_access_token()

        if not args.yes:
            if not confirm(f"Delete tag {args.tag_id}?"):
                print("Cancelled")
                return

        api_request(
            "DELETE",
            f"/api/envelopes/{args.envelope_id}/tags/{args.tag_id}",
            token,
            expected_status=[204]
        )
        print(f"Tag {args.tag_id} deleted")

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="DigiSign tag management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list command
    list_parser = subparsers.add_parser("list", help="List tags in envelope")
    list_parser.add_argument("envelope_id", help="Envelope ID")
    list_parser.set_defaults(func=cmd_list)

    # add command
    add_parser = subparsers.add_parser("add", help="Add tag to envelope")
    add_parser.add_argument("envelope_id", help="Envelope ID")
    add_parser.add_argument("--document", required=True, help="Document ID")
    add_parser.add_argument("--recipient", required=True, help="Recipient ID")
    add_parser.add_argument("--type", required=True, choices=TAG_TYPES, help="Tag type")
    # Position by placeholder
    add_parser.add_argument("--placeholder", help="Placeholder text in document")
    add_parser.add_argument("--positioning", choices=POSITIONING, help="Position relative to placeholder")
    # Position by coordinates
    add_parser.add_argument("--page", type=int, help="Page number (1-indexed)")
    add_parser.add_argument("--x", type=float, help="X position (points from left)")
    add_parser.add_argument("--y", type=float, help="Y position (points from top)")
    # Optional
    add_parser.add_argument("--width", type=float, help="Tag width")
    add_parser.add_argument("--height", type=float, help="Tag height")
    add_parser.add_argument("--required", type=bool, help="Is field required")
    add_parser.add_argument("--label", help="Field label")
    add_parser.add_argument("--group", help="Radio button group name")
    add_parser.set_defaults(func=cmd_add)

    # add-by-placeholder command
    placeholder_parser = subparsers.add_parser("add-by-placeholder", help="Add tags to all placeholder occurrences")
    placeholder_parser.add_argument("envelope_id", help="Envelope ID")
    placeholder_parser.add_argument("--recipient", required=True, help="Recipient ID")
    placeholder_parser.add_argument("--type", required=True, choices=TAG_TYPES, help="Tag type")
    placeholder_parser.add_argument("--placeholder", required=True, help="Placeholder text to find")
    placeholder_parser.add_argument("--positioning", choices=POSITIONING, default="top_left", help="Position relative to placeholder")
    placeholder_parser.add_argument("--documents", help="Comma-separated document IDs to limit scope")
    placeholder_parser.add_argument("--width", type=float, help="Tag width")
    placeholder_parser.add_argument("--height", type=float, help="Tag height")
    placeholder_parser.add_argument("--required", type=bool, help="Is field required")
    placeholder_parser.add_argument("--label", help="Field label")
    placeholder_parser.set_defaults(func=cmd_add_by_placeholder)

    # get command
    get_parser = subparsers.add_parser("get", help="Get tag details")
    get_parser.add_argument("envelope_id", help="Envelope ID")
    get_parser.add_argument("tag_id", help="Tag ID")
    get_parser.set_defaults(func=cmd_get)

    # update command
    update_parser = subparsers.add_parser("update", help="Update tag")
    update_parser.add_argument("envelope_id", help="Envelope ID")
    update_parser.add_argument("tag_id", help="Tag ID")
    update_parser.add_argument("--page", type=int, help="Page number")
    update_parser.add_argument("--x", type=float, help="X position")
    update_parser.add_argument("--y", type=float, help="Y position")
    update_parser.add_argument("--width", type=float, help="Tag width")
    update_parser.add_argument("--height", type=float, help="Tag height")
    update_parser.add_argument("--required", type=bool, help="Is field required")
    update_parser.add_argument("--label", help="Field label")
    update_parser.set_defaults(func=cmd_update)

    # delete command
    delete_parser = subparsers.add_parser("delete", help="Delete tag")
    delete_parser.add_argument("envelope_id", help="Envelope ID")
    delete_parser.add_argument("tag_id", help="Tag ID")
    delete_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    delete_parser.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
