# Embedding API Reference

Embed DigiSign signing flows directly in your application.

## Embed Types

| Type | Use Case |
|------|----------|
| Envelope | Edit/send envelope in your app |
| Recipient | Single signer signing session |
| Signing Ceremony | Multiple signers on one device |
| Detail | View envelope details |

## Endpoints

### Embed Envelope Edit/Send
```
POST /api/envelopes/{envelope}/embed
```

```json
{
  "target": "editor",
  "allowedActions": ["edit", "send"],
  "language": "cs",
  "returnUrl": "https://your-app.com/done"
}
```

### Embed Recipient Signing
```
POST /api/envelopes/{envelope}/recipients/{recipient}/embed
```

```json
{
  "returnUrl": "https://your-app.com/signed",
  "failureUrl": "https://your-app.com/error",
  "expireAt": "2024-01-15T15:00:00+01:00"
}
```

### Embed Signing Ceremony
```
POST /api/envelopes/{envelope}/embed/signing
```

```json
{
  "recipients": [
    "/api/envelopes/{env}/recipients/{rec1}",
    "/api/envelopes/{env}/recipients/{rec2}"
  ],
  "returnUrl": "https://your-app.com/done"
}
```

### Embed Envelope Detail
```
POST /api/envelopes/{envelope}/embed/detail
```

## Response

All embed endpoints return:

```json
{
  "url": "https://app.digisign.org/embed/abc123...",
  "expiresAt": "2024-01-15T15:05:00+01:00"
}
```

**URL validity:** 5 minutes by default.

## Recipient Signing

### Return URL Events

On success, redirects to `returnUrl` with query parameter:

| Event | Description |
|-------|-------------|
| `?event=success` | Signing completed |
| `?event=declined` | Signer declined |
| `?event=disapproved` | Approver rejected |

### Failure URL Events

On error, redirects to `failureUrl` with:

| Error | Description |
|-------|-------------|
| `?error=lockedError` | Envelope locked |
| `?error=bankIdClaimsMismatch` | Bank iD data mismatch |
| `?error=identificationClaimsMismatch` | Identify data mismatch |
| `?error=identificationDenied` | Identification denied |
| `?error=certificateNameMismatch` | Certificate name mismatch |
| `?error=certificateSignatureFailed` | Certificate signing failed |
| `?error=internal` | Generic error |

## Signing Ceremony

For in-person signing with multiple recipients on one device.

### Requirements

- Recipients must have `role: "in_person"`
- Signature type must be `biometric`
- No authentication required (`authenticationOnOpen: "none"`, `authenticationOnSignature: "none"`)
- Must specify `intermediaryEmail`

### Setup Example

```python
# Create envelope
envelope = create_envelope(...)

# Add recipients for in-person signing
recipient1 = add_recipient(
    envelope_id,
    role="in_person",
    name="Customer 1",
    email="customer1@example.com",
    signature_type="biometric",
    intermediary_email="sales@company.com",
    auth_on_open="none",
    auth_on_signature="none"
)

recipient2 = add_recipient(
    envelope_id,
    role="in_person",
    name="Customer 2",
    ...
)

# Send envelope
send_envelope(envelope_id)

# Get ceremony URL
embed_url = get_signing_ceremony_url(
    envelope_id,
    recipients=[recipient1["id"], recipient2["id"]],
    return_url="https://app.com/done"
)
```

## JavaScript Events

Embedded iframes post messages on state changes:

```javascript
window.addEventListener('message', (event) => {
  if (event.origin !== 'https://app.digisign.org') return;

  const data = event.data;

  // Status event
  if (data.status === 'signed') {
    console.log('Signing completed');
  }

  // Page event
  if (data.page) {
    console.log('Current page:', data.page);
  }
});
```

### Status Events

| Status | Description |
|--------|-------------|
| `signed` | Signing completed |

### Page Events

| Page | Description |
|------|-------------|
| `welcome` | Welcome screen |
| `variants` | Signature scenario selection |
| `preview` | Document preview |
| `success` | Success confirmation |
| `decline_success` | Decline confirmation |
| `disapprove_success` | Disapproval confirmation |
| `decline` | Decline reason form |
| `authenticate` | Authentication screen |

## iframe Considerations

**Not recommended:** Using iframe adds security risks (clickjacking).

**Not supported with Bank iD:** Banks block iframe embedding.

If you must use iframe:
```html
<iframe
  src="https://app.digisign.org/embed/..."
  width="100%"
  height="800"
  frameborder="0"
></iframe>
```

Prefer redirect or popup window instead.

## Timing Considerations

After sending an envelope, there's a brief async processing period (seconds to 1 minute) before embedding is available.

If you get "recipient not ready" errors, implement a retry with delay:

```python
import time

def get_embed_url_with_retry(envelope_id, recipient_id, max_retries=10):
    for i in range(max_retries):
        try:
            return get_embed_url(envelope_id, recipient_id)
        except ValidationError:
            time.sleep(2)
    raise Exception("Envelope not ready")
```

## Demo

Try embedding without coding:
- https://app.staging.digisign.org/demo/embed/envelope-signing
- https://app.staging.digisign.org/demo/embed/envelope-recipient

(Staging environment only)
