# Webhooks API Reference

Webhooks notify your application when events occur in DigiSign.

## Events

### Envelope Events

| Event | Description |
|-------|-------------|
| `envelopeSent` | Envelope was sent for signing |
| `envelopeCompleted` | All recipients signed/approved |
| `envelopeExpired` | Envelope expired |
| `envelopeDeclined` | Signer declined to sign |
| `envelopeDisapproved` | Approver rejected envelope |
| `envelopeCancelled` | Sender cancelled envelope |
| `envelopeDeleted` | Envelope was deleted |

### Recipient Events

| Event | Description |
|-------|-------------|
| `recipientSent` | Invitation sent to recipient |
| `recipientDelivered` | Recipient opened the signing link |
| `recipientNonDelivered` | Email delivery failed |
| `recipientAuthFailed` | Auth failed 3 times (locked) |
| `recipientSigned` | Recipient completed signing |
| `recipientDownloaded` | Recipient downloaded documents |
| `recipientDeclined` | Recipient declined to sign |
| `recipientDisapproved` | Approver rejected |
| `recipientCanceled` | Recipient was cancelled |

## Endpoints

### List Webhooks
```
GET /api/webhooks
```

### Create Webhook
```
POST /api/webhooks
```

```json
{
  "event": "envelopeCompleted",
  "url": "https://your-api.com/webhook",
  "status": "enabled"
}
```

### Get Webhook
```
GET /api/webhooks/{id}
```

### Update Webhook
```
PATCH /api/webhooks/{id}
```

### Delete Webhook
```
DELETE /api/webhooks/{id}
```

### Test Webhook
```
POST /api/webhooks/{id}/test
```

### List Attempts
```
GET /api/webhooks/{id}/attempts
```

### Resend Attempt
```
POST /api/webhooks/{id}/attempts/{attempt}/resend
```

## Webhook Payload

```json
{
  "id": "event-uuid",
  "event": "envelopeCompleted",
  "name": "envelope.completed",
  "time": "2024-01-15T14:30:00+01:00",
  "entityName": "envelope",
  "entityId": "envelope-uuid",
  "data": {
    "status": "completed"
  },
  "envelope": {
    "id": "envelope-uuid",
    "status": "completed"
  }
}
```

## Delivery

### Success Response
Your endpoint must return HTTP 2xx within 5 seconds.

### Retry Schedule

| Attempt | Delay |
|---------|-------|
| 1 | immediate |
| 2 | 5 minutes |
| 3 | 10 minutes |
| 4 | 30 minutes |
| 5 | 1 hour |
| 6 | 2 hours |
| 7-12 | 24 hours each |

Maximum 12 attempts over ~7 days.

## Signature Verification

DigiSign signs requests with HMAC-SHA256. Verify to ensure authenticity.

### Signature Header
```
Signature: t=1623134422,s=b15109ca56aadb4d87efdb03d258dbe40eb...
```

### Verification Steps

1. Parse header: extract `t` (timestamp) and `s` (signature)
2. Check timestamp age (reject if > 5 minutes old)
3. Build payload: `{timestamp}.{request_body}`
4. Calculate HMAC-SHA256 using webhook secret
5. Compare signatures

### Python Example

```python
import hmac
import hashlib
import time

def verify_signature(header, body, secret):
    parts = dict(p.split("=", 1) for p in header.split(","))
    timestamp = int(parts["t"])
    signature = parts["s"]

    # Check timestamp
    if time.time() - timestamp > 300:
        raise ValueError("Request too old")

    # Calculate expected signature
    payload = f"{timestamp}.{body}"
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        raise ValueError("Invalid signature")

    return True
```

### PHP Example

```php
$header = $_SERVER['HTTP_SIGNATURE'] ?? '';
$payload = file_get_contents('php://input');
$secret = 'your-webhook-secret';

if (preg_match('/t=(?<t>\d+),s=(?<s>\w+)/', $header, $m) !== 1) {
    throw new Exception('Invalid signature header');
}

$ts = (int)$m['t'];
$signature = $m['s'];

if ($ts < (time() - 300)) {
    throw new Exception('Request too old');
}

$expected = hash_hmac('sha256', $ts . '.' . $payload, $secret);

if (!hash_equals($expected, $signature)) {
    throw new Exception('Invalid signature');
}
```

## OAuth 2.0 Security

Optionally secure webhooks with OAuth:

```json
{
  "event": "envelopeCompleted",
  "url": "https://your-api.com/webhook",
  "oAuthTokenEndpoint": "https://your-api.com/oauth/token",
  "oAuthClientId": "client-id",
  "oAuthClientSecret": "client-secret",
  "oAuthScopes": ["read", "write"]
}
```

DigiSign will obtain a token before each webhook call.

## Automatic Deactivation

Webhooks are auto-disabled if:
- More than 75% of deliveries fail over 7 days
- Webhook is older than 7 days
- More than 10 attempts made

You'll receive an email notification before and after deactivation.

## Idempotency

Events may be delivered multiple times. Handle duplicates by:
- Storing processed event IDs
- Making handlers idempotent
- Using the `id` field to detect duplicates
