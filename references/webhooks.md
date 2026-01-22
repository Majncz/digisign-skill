# Webhooks API Reference

Webhooks notify your application in real-time when events occur in DigiSign. This is the best way to track envelope status changes rather than polling.

## Events

### Envelope Events

| Event | Description |
|-------|-------------|
| `envelopeSent` | Envelope was sent for signing |
| `envelopeCompleted` | All recipients signed/approved |
| `envelopeExpired` | Envelope expired (deadline passed) |
| `envelopeDeclined` | A signer declined to sign |
| `envelopeDisapproved` | An approver rejected the envelope |
| `envelopeCancelled` | Sender cancelled the envelope |
| `envelopeDeleted` | Envelope was deleted |

### Recipient Events

| Event | Description |
|-------|-------------|
| `recipientSent` | Invitation sent to recipient |
| `recipientDelivered` | Recipient opened the signing link |
| `recipientNonDelivered` | Email delivery failed (bad address, etc.) |
| `recipientAuthFailed` | Authentication failed 3 times (locked out) |
| `recipientSigned` | Recipient completed signing |
| `recipientDownloaded` | Recipient downloaded signed documents |
| `recipientDeclined` | Recipient declined to sign |
| `recipientDisapproved` | Approver rejected |
| `recipientCanceled` | Recipient was cancelled |

## Endpoints

### List Webhooks
```
GET /api/webhooks
```

**Response:**
```json
{
  "items": [
    {
      "id": "3974d252-b027-46df-9fd8-ddae54bc9ab9",
      "event": "envelopeCompleted",
      "url": "https://your-api.com/webhook",
      "status": "enabled",
      "secret": "wh_secret_abc123...",
      "createdAt": "2024-01-15T10:30:00+01:00"
    }
  ],
  "count": 5,
  "page": 1,
  "itemsPerPage": 30
}
```

### Create Webhook
```
POST /api/webhooks
```

**Request:**
```json
{
  "event": "envelopeCompleted",
  "url": "https://your-api.com/webhook",
  "status": "enabled"
}
```

**Response:**
```json
{
  "id": "3974d252-b027-46df-9fd8-ddae54bc9ab9",
  "event": "envelopeCompleted",
  "url": "https://your-api.com/webhook",
  "status": "enabled",
  "secret": "wh_secret_abc123def456...",
  "createdAt": "2024-01-15T10:30:00+01:00"
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event` | string | Yes | Event to listen for |
| `url` | string | Yes | Your endpoint URL (HTTPS recommended) |
| `status` | string | No | `enabled` (default) or `disabled` |
| `oAuthTokenEndpoint` | string | No | OAuth token endpoint |
| `oAuthClientId` | string | No | OAuth client ID |
| `oAuthClientSecret` | string | No | OAuth client secret |
| `oAuthScopes` | array | No | OAuth scopes |

### Get Webhook
```
GET /api/webhooks/{id}
```

Returns webhook details including the `secret` for signature verification.

### Update Webhook
```
PUT /api/webhooks/{id}
```

### Delete Webhook
```
DELETE /api/webhooks/{id}
```

### Test Webhook
```
POST /api/webhooks/{id}/test
```

Sends a test event to your webhook URL. Useful for verifying connectivity and signature handling.

### List Delivery Attempts
```
GET /api/webhooks/{id}/attempts
```

**Response:**
```json
{
  "items": [
    {
      "id": "attempt-uuid",
      "status": "success",
      "httpCode": 200,
      "requestHeaders": {...},
      "requestBody": "{...}",
      "responseHeaders": {...},
      "responseBody": "OK",
      "createdAt": "2024-01-15T14:30:00+01:00",
      "nextAttemptAt": null
    }
  ],
  "count": 3,
  "page": 1,
  "itemsPerPage": 30
}
```

### Resend Failed Attempt
```
POST /api/webhooks/{webhook_id}/attempts/{attempt_id}/resend
```

Manually retry a failed delivery attempt.

## Webhook Payload

DigiSign sends a POST request to your URL with this JSON body:

```json
{
  "id": "3974d252-b027-46df-9fd8-ddae54bc9ab9",
  "event": "envelopeCompleted",
  "name": "envelope.completed",
  "time": "2024-01-15T14:30:00+01:00",
  "entityName": "envelope",
  "entityId": "4fcf171c-4522-4a53-8a72-784e1dd36c2a",
  "data": {
    "status": "completed"
  },
  "envelope": {
    "id": "4fcf171c-4522-4a53-8a72-784e1dd36c2a",
    "status": "completed"
  }
}
```

**Payload Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique event ID (use for deduplication) |
| `event` | string | Event type (e.g., `envelopeCompleted`) |
| `name` | string | Event name in dot notation (`envelope.completed`) |
| `time` | datetime | When the event occurred (ISO 8601) |
| `entityName` | string | Type of entity (`envelope` or `recipient`) |
| `entityId` | UUID | ID of the affected entity |
| `data` | object | Event-specific data |
| `envelope` | object | Basic envelope info (for backwards compatibility) |

### Event-Specific Data

**Envelope events:**
```json
{
  "data": {
    "status": "completed"  // New envelope status
  }
}
```

**Recipient events:**
```json
{
  "data": {
    "recipientId": "recipient-uuid",
    "recipientStatus": "signed"
  }
}
```

## Delivery

### Requirements
- Your endpoint must return HTTP 2xx within **5 seconds**
- Use HTTPS (recommended for production)
- Handle duplicate deliveries (see Idempotency section)

### Success Response
Any HTTP 2xx status code is considered successful:
```
HTTP/1.1 200 OK
Content-Type: text/plain

OK
```

### Failure Handling
Non-2xx responses or timeouts trigger retry logic.

## Retry Schedule

Failed deliveries are retried with exponential backoff:

| Attempt | Delay from Previous | Total Time |
|---------|---------------------|------------|
| 1 | Immediate | 0 |
| 2 | 5 minutes | 5 min |
| 3 | 10 minutes | 15 min |
| 4 | 30 minutes | 45 min |
| 5 | 1 hour | 1h 45min |
| 6 | 2 hours | 3h 45min |
| 7 | 24 hours | ~1 day |
| 8 | 24 hours | ~2 days |
| 9 | 24 hours | ~3 days |
| 10 | 24 hours | ~4 days |
| 11 | 24 hours | ~5 days |
| 12 | 24 hours | ~6 days |

Maximum **12 attempts** over approximately **7 days**.

If a webhook is paused and resumed before the next retry, retries continue as scheduled.

## Signature Verification

DigiSign signs all webhook requests with HMAC-SHA256. Verify signatures to:
- Ensure the request came from DigiSign
- Detect tampering
- Prevent replay attacks

### Signature Header
```
Signature: t=1623134422,s=b15109ca56aadb4d87efdb03d258dbe40eb...
```

| Part | Description |
|------|-------------|
| `t` | Unix timestamp when signature was created |
| `s` | HMAC-SHA256 signature (hex-encoded) |

### Verification Steps

1. **Parse the header**: Extract `t` (timestamp) and `s` (signature)
2. **Check timestamp**: Reject if older than 5 minutes (prevents replay attacks)
3. **Build signature base**: Concatenate `{timestamp}.{request_body}`
4. **Calculate expected signature**: HMAC-SHA256 with webhook secret as key
5. **Compare signatures**: Use constant-time comparison

### Python Example

```python
import hmac
import hashlib
import time
from flask import Flask, request, abort

app = Flask(__name__)
WEBHOOK_SECRET = "your-webhook-secret"

def verify_webhook_signature(signature_header: str, body: bytes, secret: str) -> bool:
    """Verify DigiSign webhook signature."""
    try:
        # Parse header
        parts = dict(p.split("=", 1) for p in signature_header.split(","))
        timestamp = int(parts["t"])
        signature = parts["s"]
    except (KeyError, ValueError):
        return False

    # Check timestamp (5 minute tolerance)
    if abs(time.time() - timestamp) > 300:
        return False

    # Calculate expected signature
    payload = f"{timestamp}.{body.decode()}"
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    # Constant-time comparison
    return hmac.compare_digest(expected, signature)

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    signature = request.headers.get("Signature", "")

    if not verify_webhook_signature(signature, request.data, WEBHOOK_SECRET):
        abort(401, "Invalid signature")

    event = request.json
    print(f"Received event: {event['event']} for {event['entityId']}")

    # Process the event...

    return "OK", 200
```

### JavaScript/Node.js Example

```javascript
const crypto = require('crypto');
const express = require('express');

const app = express();
const WEBHOOK_SECRET = 'your-webhook-secret';

app.use(express.raw({ type: 'application/json' }));

function verifyWebhookSignature(signatureHeader, body, secret) {
  const parts = Object.fromEntries(
    signatureHeader.split(',').map(p => p.split('='))
  );

  const timestamp = parseInt(parts.t);
  const signature = parts.s;

  // Check timestamp (5 minute tolerance)
  if (Math.abs(Date.now() / 1000 - timestamp) > 300) {
    return false;
  }

  // Calculate expected signature
  const payload = `${timestamp}.${body.toString()}`;
  const expected = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  // Constant-time comparison
  return crypto.timingSafeEqual(
    Buffer.from(expected),
    Buffer.from(signature)
  );
}

app.post('/webhook', (req, res) => {
  const signature = req.headers['signature'] || '';

  if (!verifyWebhookSignature(signature, req.body, WEBHOOK_SECRET)) {
    return res.status(401).send('Invalid signature');
  }

  const event = JSON.parse(req.body);
  console.log(`Received event: ${event.event} for ${event.entityId}`);

  // Process the event...

  res.status(200).send('OK');
});
```

### PHP Example

```php
<?php
$webhookSecret = 'your-webhook-secret';
$signatureHeader = $_SERVER['HTTP_SIGNATURE'] ?? '';
$payload = file_get_contents('php://input');

function verifyWebhookSignature(string $header, string $body, string $secret): bool {
    if (preg_match('/t=(?<t>\d+),s=(?<s>\w+)/', $header, $matches) !== 1) {
        return false;
    }

    $timestamp = (int) $matches['t'];
    $signature = $matches['s'];

    // Check timestamp (5 minute tolerance)
    if (abs(time() - $timestamp) > 300) {
        return false;
    }

    // Calculate expected signature
    $expected = hash_hmac('sha256', $timestamp . '.' . $body, $secret);

    // Constant-time comparison
    return hash_equals($expected, $signature);
}

if (!verifyWebhookSignature($signatureHeader, $payload, $webhookSecret)) {
    http_response_code(401);
    die('Invalid signature');
}

$event = json_decode($payload, true);
error_log("Received event: {$event['event']} for {$event['entityId']}");

// Process the event...

echo 'OK';
```

## OAuth 2.0 Security

Optionally secure your webhook endpoint with OAuth 2.0:

```json
{
  "event": "envelopeCompleted",
  "url": "https://your-api.com/webhook",
  "oAuthTokenEndpoint": "https://your-api.com/oauth/token",
  "oAuthClientId": "digisign-webhook",
  "oAuthClientSecret": "your-client-secret",
  "oAuthScopes": ["webhook:write"]
}
```

DigiSign will:
1. Request an access token from your OAuth endpoint before each webhook call
2. Include the token in the `Authorization: Bearer {token}` header
3. Cache tokens based on `expires_in`

Your OAuth endpoint should support the client credentials grant:
```
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&client_id=...&client_secret=...&scope=webhook:write
```

## Automatic Deactivation

DigiSign automatically disables poorly-performing webhooks to prevent wasted resources.

### Deactivation Criteria
All conditions must be met:
- More than **75% of deliveries failed** in the last 7 days
- Webhook is older than **7 days**
- More than **10 delivery attempts** were made

### Notification Process
1. **Warning email** sent when criteria are approaching
2. **7-day grace period** to fix the issue
3. **Deactivation email** sent when webhook is disabled

To reactivate:
1. Fix your endpoint issues
2. Re-enable the webhook via API or selfcare

## Idempotency

Webhooks may be delivered multiple times due to:
- Network issues
- Your endpoint timing out
- Retry logic

**Always make your handlers idempotent:**

```python
processed_events = set()  # Use a database in production

def handle_webhook(event):
    event_id = event['id']

    # Skip if already processed
    if event_id in processed_events:
        return  # Already handled

    # Process the event
    if event['event'] == 'envelopeCompleted':
        download_signed_documents(event['entityId'])

    # Mark as processed
    processed_events.add(event_id)
```

## Best Practices

1. **Respond quickly** - Return 200 OK immediately, process asynchronously
2. **Verify signatures** - Always verify HMAC signatures in production
3. **Handle duplicates** - Store processed event IDs
4. **Use HTTPS** - Secure your webhook endpoint
5. **Log everything** - Log received events for debugging
6. **Monitor failures** - Alert on repeated delivery failures
7. **Test thoroughly** - Use the test endpoint during development

## CLI Script Usage

```bash
# Create webhook
python scripts/webhook.py create --event envelopeCompleted --url "https://your-api.com/webhook"

# List webhooks
python scripts/webhook.py list

# Test webhook
python scripts/webhook.py test <webhook_id>

# View delivery attempts
python scripts/webhook.py attempts <webhook_id>

# Resend failed attempt
python scripts/webhook.py resend <webhook_id> <attempt_id>

# Verify signature locally
python scripts/webhook.py verify-signature \
  --signature "t=1623134422,s=abc123..." \
  --body '{"event":"envelopeCompleted",...}' \
  --secret "your-webhook-secret"
```
