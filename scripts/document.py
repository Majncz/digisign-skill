#!/usr/bin/env python3
"""Document management for DigiSign API."""

import argparse
import sys

from utils import (
    get_access_token, api_request, api_request_binary, upload_file,
    print_json, print_error, confirm,
    DigiSignError, ValidationError
)


def cmd_upload(args):
    """Upload a file."""
    try:
        token = get_access_token()
        result = upload_file(args.file, token)
        print_json(result)

    except FileNotFoundError:
        print_error(f"File not found: {args.file}")
        sys.exit(1)
    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_add(args):
    """Add uploaded file as document to envelope."""
    try:
        token = get_access_token()

        # Build file IRI if not already a full path
        file_iri = args.file_id
        if not file_iri.startswith("/api/"):
            file_iri = f"/api/files/{args.file_id}"

        data = {
            "file": file_iri,
            "name": args.name,
        }

        if args.position is not None:
            data["position"] = args.position

        result = api_request(
            "POST",
            f"/api/envelopes/{args.envelope_id}/documents",
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


def cmd_list(args):
    """List documents in envelope."""
    try:
        token = get_access_token()
        result = api_request("GET", f"/api/envelopes/{args.envelope_id}/documents", token)

        documents = result if isinstance(result, list) else result.get("hydra:member", result.get("member", []))
        print_json(documents)

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_get(args):
    """Get document details."""
    try:
        token = get_access_token()
        result = api_request(
            "GET",
            f"/api/envelopes/{args.envelope_id}/documents/{args.document_id}",
            token
        )
        print_json(result)

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_update(args):
    """Update document."""
    try:
        token = get_access_token()

        data = {}
        if args.name:
            data["name"] = args.name
        if args.position is not None:
            data["position"] = args.position

        result = api_request(
            "PATCH",
            f"/api/envelopes/{args.envelope_id}/documents/{args.document_id}",
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
    """Remove document from envelope."""
    try:
        token = get_access_token()

        if not args.yes:
            if not confirm(f"Remove document {args.document_id} from envelope?"):
                print("Cancelled")
                return

        api_request(
            "DELETE",
            f"/api/envelopes/{args.envelope_id}/documents/{args.document_id}",
            token,
            expected_status=[204]
        )
        print(f"Document {args.document_id} removed")

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_download(args):
    """Download specific document."""
    try:
        token = get_access_token()

        data = api_request_binary(
            "GET",
            f"/api/envelopes/{args.envelope_id}/documents/{args.document_id}/download",
            token
        )

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
    """Get download URL for specific document."""
    try:
        token = get_access_token()
        result = api_request(
            "GET",
            f"/api/envelopes/{args.envelope_id}/documents/{args.document_id}/download-url",
            token
        )
        print_json(result)

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="DigiSign document management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # upload command
    upload_parser = subparsers.add_parser("upload", help="Upload a file")
    upload_parser.add_argument("file", help="Path to file to upload")
    upload_parser.set_defaults(func=cmd_upload)

    # add command
    add_parser = subparsers.add_parser("add", help="Add uploaded file as document to envelope")
    add_parser.add_argument("envelope_id", help="Envelope ID")
    add_parser.add_argument("--file-id", required=True, help="File ID from upload")
    add_parser.add_argument("--name", required=True, help="Document name (displayed to signers)")
    add_parser.add_argument("--position", type=int, help="Document order position")
    add_parser.set_defaults(func=cmd_add)

    # list command
    list_parser = subparsers.add_parser("list", help="List documents in envelope")
    list_parser.add_argument("envelope_id", help="Envelope ID")
    list_parser.set_defaults(func=cmd_list)

    # get command
    get_parser = subparsers.add_parser("get", help="Get document details")
    get_parser.add_argument("envelope_id", help="Envelope ID")
    get_parser.add_argument("document_id", help="Document ID")
    get_parser.set_defaults(func=cmd_get)

    # update command
    update_parser = subparsers.add_parser("update", help="Update document")
    update_parser.add_argument("envelope_id", help="Envelope ID")
    update_parser.add_argument("document_id", help="Document ID")
    update_parser.add_argument("--name", help="Document name")
    update_parser.add_argument("--position", type=int, help="Document order position")
    update_parser.set_defaults(func=cmd_update)

    # delete command
    delete_parser = subparsers.add_parser("delete", help="Remove document from envelope")
    delete_parser.add_argument("envelope_id", help="Envelope ID")
    delete_parser.add_argument("document_id", help="Document ID")
    delete_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    delete_parser.set_defaults(func=cmd_delete)

    # download command
    download_parser = subparsers.add_parser("download", help="Download specific document")
    download_parser.add_argument("envelope_id", help="Envelope ID")
    download_parser.add_argument("document_id", help="Document ID")
    download_parser.add_argument("--output", "-o", help="Output file path")
    download_parser.set_defaults(func=cmd_download)

    # download-url command
    url_parser = subparsers.add_parser("download-url", help="Get download URL for document")
    url_parser.add_argument("envelope_id", help="Envelope ID")
    url_parser.add_argument("document_id", help="Document ID")
    url_parser.set_defaults(func=cmd_download_url)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
