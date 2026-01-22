#!/usr/bin/env python3
"""Recipient management for DigiSign API."""

import argparse
import json
import sys

from utils import (
    get_access_token, api_request,
    print_json, print_error, confirm,
    DigiSignError, ValidationError
)


ROLES = ["signer", "in_person", "cc", "approver", "autosign", "semi_autosign"]
SIGNATURE_TYPES = ["simple", "biometric", "bank_id_sign", "certificate"]
CHANNELS = ["email", "sms", "none"]
AUTH_METHODS = ["none", "sms", "bank_id", "identification"]


def cmd_list(args):
    """List recipients in envelope."""
    try:
        token = get_access_token()
        result = api_request("GET", f"/api/envelopes/{args.envelope_id}/recipients", token)

        recipients = result if isinstance(result, list) else result.get("items", result.get("hydra:member", result.get("member", [])))
        print_json(recipients)

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_add(args):
    """Add recipient to envelope."""
    try:
        token = get_access_token()

        data = {
            "role": args.role,
            "name": args.name,
        }

        if args.email:
            data["email"] = args.email
        if args.mobile:
            data["mobile"] = args.mobile
        if args.position is not None:
            data["position"] = args.position
        if args.signature_type:
            data["signatureType"] = args.signature_type
        if args.channel_for_signer:
            data["channelForSigner"] = args.channel_for_signer
        if args.channel_for_download:
            data["channelForDownload"] = args.channel_for_download
        if args.auth_on_open:
            data["authenticationOnOpen"] = args.auth_on_open
        if args.auth_on_signature:
            data["authenticationOnSignature"] = args.auth_on_signature
        if args.scenario:
            scenario_iri = args.scenario
            if not scenario_iri.startswith("/api/"):
                scenario_iri = f"/api/account/signature-scenarios/{args.scenario}"
            data["scenario"] = scenario_iri
        if args.intermediary_email:
            data["intermediaryEmail"] = args.intermediary_email
        if args.language:
            data["language"] = args.language
        if args.metadata:
            data["metadata"] = json.loads(args.metadata)

        result = api_request(
            "POST",
            f"/api/envelopes/{args.envelope_id}/recipients",
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
    """Get recipient details."""
    try:
        token = get_access_token()
        result = api_request(
            "GET",
            f"/api/envelopes/{args.envelope_id}/recipients/{args.recipient_id}",
            token
        )
        print_json(result)

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_update(args):
    """Update recipient."""
    try:
        token = get_access_token()

        data = {}
        if args.name:
            data["name"] = args.name
        if args.email:
            data["email"] = args.email
        if args.mobile:
            data["mobile"] = args.mobile
        if args.position is not None:
            data["position"] = args.position
        if args.signature_type:
            data["signatureType"] = args.signature_type
        if args.channel_for_signer:
            data["channelForSigner"] = args.channel_for_signer
        if args.channel_for_download:
            data["channelForDownload"] = args.channel_for_download
        if args.auth_on_open:
            data["authenticationOnOpen"] = args.auth_on_open
        if args.auth_on_signature:
            data["authenticationOnSignature"] = args.auth_on_signature
        if args.language:
            data["language"] = args.language
        if args.metadata:
            data["metadata"] = json.loads(args.metadata)

        result = api_request(
            "PUT",
            f"/api/envelopes/{args.envelope_id}/recipients/{args.recipient_id}",
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
    """Remove recipient from envelope."""
    try:
        token = get_access_token()

        if not args.yes:
            if not confirm(f"Remove recipient {args.recipient_id} from envelope?"):
                print("Cancelled")
                return

        api_request(
            "DELETE",
            f"/api/envelopes/{args.envelope_id}/recipients/{args.recipient_id}",
            token,
            expected_status=[204]
        )
        print(f"Recipient {args.recipient_id} removed")

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_resend(args):
    """Resend signing invitation to recipient."""
    try:
        token = get_access_token()

        result = api_request(
            "POST",
            f"/api/envelopes/{args.envelope_id}/recipients/{args.recipient_id}/resend",
            token,
            expected_status=[200, 204]
        )
        if result:
            print_json(result)
        else:
            print(f"Invitation resent to recipient {args.recipient_id}")

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def cmd_autosign(args):
    """Trigger automatic signature for semi_autosign recipient."""
    try:
        token = get_access_token()

        if not args.yes:
            if not confirm(f"Trigger autosign for recipient {args.recipient_id}?"):
                print("Cancelled")
                return

        result = api_request(
            "POST",
            f"/api/envelopes/{args.envelope_id}/recipients/{args.recipient_id}/autosign",
            token,
            expected_status=[200, 204]
        )
        if result:
            print_json(result)
        else:
            print(f"Autosign triggered for recipient {args.recipient_id}")

    except DigiSignError as e:
        print_error(str(e))
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="DigiSign recipient management")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list command
    list_parser = subparsers.add_parser("list", help="List recipients in envelope")
    list_parser.add_argument("envelope_id", help="Envelope ID")
    list_parser.set_defaults(func=cmd_list)

    # add command
    add_parser = subparsers.add_parser("add", help="Add recipient to envelope")
    add_parser.add_argument("envelope_id", help="Envelope ID")
    add_parser.add_argument("--role", required=True, choices=ROLES, help="Recipient role")
    add_parser.add_argument("--name", required=True, help="Recipient name")
    add_parser.add_argument("--email", help="Recipient email")
    add_parser.add_argument("--mobile", help="Recipient mobile phone (E.164 format: +420...)")
    add_parser.add_argument("--position", type=int, help="Signing order position")
    add_parser.add_argument("--signature-type", choices=SIGNATURE_TYPES, help="Signature type")
    add_parser.add_argument("--channel-for-signer", choices=CHANNELS, help="How to deliver signing invitation")
    add_parser.add_argument("--channel-for-download", choices=CHANNELS, help="How to deliver completed docs")
    add_parser.add_argument("--auth-on-open", choices=AUTH_METHODS, help="Authentication when opening")
    add_parser.add_argument("--auth-on-signature", choices=AUTH_METHODS, help="Authentication when signing")
    add_parser.add_argument("--scenario", help="Signature scenario ID")
    add_parser.add_argument("--intermediary-email", help="Intermediary email (for in_person role)")
    add_parser.add_argument("--language", help="Recipient language (cs, en, sk, pl, etc.)")
    add_parser.add_argument("--metadata", help="Custom metadata (JSON object)")
    add_parser.set_defaults(func=cmd_add)

    # get command
    get_parser = subparsers.add_parser("get", help="Get recipient details")
    get_parser.add_argument("envelope_id", help="Envelope ID")
    get_parser.add_argument("recipient_id", help="Recipient ID")
    get_parser.set_defaults(func=cmd_get)

    # update command
    update_parser = subparsers.add_parser("update", help="Update recipient")
    update_parser.add_argument("envelope_id", help="Envelope ID")
    update_parser.add_argument("recipient_id", help="Recipient ID")
    update_parser.add_argument("--name", help="Recipient name")
    update_parser.add_argument("--email", help="Recipient email")
    update_parser.add_argument("--mobile", help="Recipient mobile phone")
    update_parser.add_argument("--position", type=int, help="Signing order position")
    update_parser.add_argument("--signature-type", choices=SIGNATURE_TYPES, help="Signature type")
    update_parser.add_argument("--channel-for-signer", choices=CHANNELS, help="How to deliver signing invitation")
    update_parser.add_argument("--channel-for-download", choices=CHANNELS, help="How to deliver completed docs")
    update_parser.add_argument("--auth-on-open", choices=AUTH_METHODS, help="Authentication when opening")
    update_parser.add_argument("--auth-on-signature", choices=AUTH_METHODS, help="Authentication when signing")
    update_parser.add_argument("--language", help="Recipient language")
    update_parser.add_argument("--metadata", help="Custom metadata (JSON object)")
    update_parser.set_defaults(func=cmd_update)

    # delete command
    delete_parser = subparsers.add_parser("delete", help="Remove recipient from envelope")
    delete_parser.add_argument("envelope_id", help="Envelope ID")
    delete_parser.add_argument("recipient_id", help="Recipient ID")
    delete_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    delete_parser.set_defaults(func=cmd_delete)

    # resend command
    resend_parser = subparsers.add_parser("resend", help="Resend signing invitation")
    resend_parser.add_argument("envelope_id", help="Envelope ID")
    resend_parser.add_argument("recipient_id", help="Recipient ID")
    resend_parser.set_defaults(func=cmd_resend)

    # autosign command
    autosign_parser = subparsers.add_parser("autosign", help="Trigger automatic signature (semi_autosign)")
    autosign_parser.add_argument("envelope_id", help="Envelope ID")
    autosign_parser.add_argument("recipient_id", help="Recipient ID")
    autosign_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    autosign_parser.set_defaults(func=cmd_autosign)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
