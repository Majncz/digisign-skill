---
name: digisign
description: Czech electronic signature API integration for DigiSign. Use when the user needs to create, send, and manage digital signature envelopes, upload documents for signing, track signature status, or integrate embedded signing flows. Supports multiple signature types, webhooks for status tracking, and Czech Bank iD verification. Triggers on mentions of DigiSign, elektronicky podpis, digital signatures, envelope signing, or document signing workflows.
---

# DigiSign API

Czech electronic signature service API integration.

## Quick Start

### Environment Setup
```bash
export DIGISIGN_ACCESS_KEY="your-access-key"
export DIGISIGN_SECRET_KEY="your-secret-key"
# Optional: use staging for testing
# export DIGISIGN_API_URL="https://api.staging.digisign.org"
```

### Authenticate
```bash
python scripts/auth.py get-token --save
```

### Create and Send Envelope
```bash
# 1. Create envelope
python scripts/envelope.py create --name "Contract" --email-body "Please sign the attached contract."

# 2. Upload document
python scripts/document.py upload contract.pdf

# 3. Add document to envelope
python scripts/document.py add <envelope_id> --file-id <file_id> --name "Contract Agreement"

# 4. Add recipient
python scripts/recipient.py add <envelope_id> --role signer --name "John Doe" --email "john@example.com"

# 5. Add signature tag
python scripts/tag.py add <envelope_id> --document <doc_id> --recipient <rec_id> --type signature --placeholder "{{signature}}"

# 6. Send (CAUTION: incurs charges, sends real emails)
python scripts/envelope.py send <envelope_id> --yes
```

## API Basics

- **Production URL**: `https://api.digisign.org`
- **Staging URL**: `https://api.staging.digisign.org`
- **Auth**: Bearer token (JWT) from accessKey/secretKey exchange
- **Docs**: https://api.digisign.org/api/docs

### API Key Setup
1. Log into DigiSign selfcare
2. Go to Settings > For Developers > API Keys
3. Create new API key with required permissions
4. Save accessKey and secretKey securely

## Scripts Reference

| Script | Commands | Description |
|--------|----------|-------------|
| `auth.py` | get-token, status, clear | Token management |
| `envelope.py` | list, get, create, update, delete, send, cancel, download, download-url | Envelope operations |
| `document.py` | upload, add, list, get, update, delete, download, download-url | Document management |
| `recipient.py` | list, add, get, update, delete, resend, autosign | Recipient management |
| `tag.py` | list, add, add-by-placeholder, get, update, delete | Signature tag operations |
| `webhook.py` | list, create, get, update, delete, test, attempts, resend, verify-signature | Webhook management |
| `embed.py` | envelope, recipient, signing, detail | Embedding URLs |

## Common Workflows

### Track Envelope Status
```bash
# List all sent envelopes
python scripts/envelope.py list --status sent

# Get specific envelope details
python scripts/envelope.py get <envelope_id>

# Download signed documents
python scripts/envelope.py download <envelope_id> --output signed.pdf
```

### Setup Webhook for Completion
```bash
# Create webhook for completed envelopes
python scripts/webhook.py create --event envelopeCompleted --url "https://your-api.com/webhook"

# List webhooks
python scripts/webhook.py list
```

### Embed Signing in Your App
```bash
# Get embed URL for signing session
python scripts/embed.py recipient <envelope_id> <recipient_id> --return-url "https://your-app.com/done"
```

## Recipient Roles

| Role | Description |
|------|-------------|
| `signer` | Remote signer - receives email with signing link |
| `in_person` | Signs in person on intermediary's device |
| `cc` | Copy recipient - receives completed documents |
| `approver` | Approves or rejects document |
| `autosign` | Automatic signature with company seal |
| `semi_autosign` | Triggered automatic signature via API |

## Tag Types

| Type | Description |
|------|-------------|
| `signature` | Signature field (required for signers) |
| `approval` | Approval stamp field |
| `text` | Text input field |
| `document` | ID document photos |
| `attachment` | File attachment field |
| `checkbox` | Checkbox field |
| `radio_button` | Radio button (use with --group) |
| `date_of_signature` | Auto-filled signature date |

## Tag Positioning

### By Placeholder (Recommended)
```bash
# Place signature where {{sign_here}} appears in PDF
python scripts/tag.py add <env_id> --document <doc_id> --recipient <rec_id> \
  --type signature --placeholder "{{sign_here}}" --positioning center
```

Positioning options: `top_left`, `top_center`, `top_right`, `middle_left`, `center`, `middle_right`, `bottom_left`, `bottom_center`, `bottom_right`

### By Coordinates
```bash
# Place at specific position (72 points = 1 inch)
python scripts/tag.py add <env_id> --document <doc_id> --recipient <rec_id> \
  --type signature --page 1 --x 100 --y 500
```

## Envelope Statuses

| Status | Description |
|--------|-------------|
| `draft` | Not yet sent, can be edited |
| `sent` | Sent, waiting for signatures |
| `completed` | All recipients signed |
| `expired` | Deadline passed without completion |
| `declined` | Signer declined to sign |
| `cancelled` | Cancelled by sender |

## Signature Types

| Type | Description |
|------|-------------|
| `simple` | Simple electronic signature |
| `biometric` | Handwritten signature capture |
| `bank_id_sign` | Bank iD Sign (qualified) |
| `certificate` | Certificate-based signature |

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Bad request - check violations field |
| 401 | Authentication failed - get new token |
| 403 | Operation forbidden |
| 404 | Resource not found |
| 422 | Validation error - check violations |
| 429 | Rate limit exceeded |

## Czech-Specific Notes

### Bank iD (Bankovni identita)
- Czech national identity verification via banks
- Use `--auth-on-open bank_id` or `--auth-on-signature bank_id`
- Verifies signer identity through their bank

### Qualified Electronic Signature
- Use `--signature-type bank_id_sign` for legally binding qualified signatures
- Requires Bank iD verification

### Audit Log
- Every envelope includes an audit log (protokol)
- Download with `--include-log true` or `--output-format only_log`

## Token Management

```bash
# Get new token (valid ~24 hours)
python scripts/auth.py get-token --save

# Check token status
python scripts/auth.py status

# Token file location
~/.digisign/token.json
```

## Webhook Security

### Signature Verification
DigiSign signs webhook requests with HMAC-SHA256. Verify with:
```bash
python scripts/webhook.py verify-signature \
  --signature "t=1623134422,s=b15109ca..." \
  --body '{"event":"envelopeCompleted",...}' \
  --secret "your-webhook-secret"
```

### Webhook Events
- Envelope: `envelopeSent`, `envelopeCompleted`, `envelopeExpired`, `envelopeDeclined`, `envelopeDisapproved`, `envelopeCancelled`, `envelopeDeleted`
- Recipient: `recipientSent`, `recipientDelivered`, `recipientNonDelivered`, `recipientAuthFailed`, `recipientSigned`, `recipientDownloaded`, `recipientDeclined`, `recipientDisapproved`, `recipientCanceled`

## Cost Warning

DigiSign charges per envelope **sent**. These operations are FREE:
- Creating/editing draft envelopes
- Uploading documents
- Managing recipients and tags
- Webhook setup
- Generating embed URLs

The `send` command requires confirmation and will bill your account.

## References

- [envelopes.md](references/envelopes.md) - Envelope lifecycle and attributes
- [recipients.md](references/recipients.md) - Recipient roles and options
- [tags.md](references/tags.md) - Tag positioning and types
- [webhooks.md](references/webhooks.md) - Event list and verification
- [embedding.md](references/embedding.md) - Embedded signing integration
