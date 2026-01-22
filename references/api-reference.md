# API Reference

Complete endpoint reference for the DigiSign REST API.

## Base URLs

| Environment | URL |
|-------------|-----|
| Production | `https://api.digisign.org` |
| Staging | `https://api.staging.digisign.org` |

## Common Patterns

### Request Headers
```http
Authorization: Bearer {token}
Content-Type: application/json
Accept: application/json
Accept-Language: en  # Optional: en, cs, sk, pl
```

### Pagination Response
All list endpoints return:
```json
{
  "items": [...],
  "count": 127,
  "page": 1,
  "itemsPerPage": 30
}
```

### Pagination Parameters
| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `page` | integer | 1 | - | Page number |
| `itemsPerPage` | integer | 30 | 500 | Items per page |

### Filter Operators
Append to field name in query string:

| Operator | Example | Description |
|----------|---------|-------------|
| `[eq]` | `status[eq]=completed` | Equals |
| `[neq]` | `status[neq]=draft` | Not equals |
| `[in]` | `status[in][]=sent&status[in][]=completed` | In array |
| `[contains]` | `name[contains]=contract` | Contains |
| `[starts_with]` | `email[starts_with]=john` | Starts with |
| `[gt]` | `createdAt[gt]=2024-01-01` | Greater than |
| `[gte]` | `createdAt[gte]=2024-01-01` | Greater than or equal |
| `[lt]` | `validTo[lt]=2024-12-31` | Less than |
| `[lte]` | `validTo[lte]=2024-12-31` | Less than or equal |

### Sorting
```
order[createdAt]=desc
order[updatedAt]=asc
```

### IRI References
When referencing other resources, use IRI format:
```json
{
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "document": "/api/envelopes/{envelope_id}/documents/{document_id}",
  "file": "/api/files/{file_id}"
}
```

### Error Response
```json
{
  "type": "https://tools.ietf.org/html/rfc2616#section-10",
  "title": "An error occurred",
  "status": 400,
  "violations": [
    {
      "propertyPath": "email",
      "message": "This value is not a valid email address."
    }
  ]
}
```

---

## Authentication

### Get Token
```
POST /api/auth-token
```

**Request:**
```json
{
  "accessKey": "string",
  "secretKey": "string"
}
```

**Response:**
```json
{
  "token": "string",
  "exp": 1682572132,
  "iat": 1682485732
}
```

---

## Account

### Get Account
```
GET /api/account
```

### Get Account Statistics
```
GET /api/account/statistics
```

### Get Account Billing
```
GET /api/account/billing
```

---

## Envelopes

### List Envelopes
```
GET /api/envelopes
```

**Query Parameters:**
- `status[eq]` - Filter by status (draft, sent, completed, expired, declined, disapproved, cancelled)
- `createdAt[gte]`, `createdAt[lte]` - Filter by creation date
- `updatedAt[gte]`, `updatedAt[lte]` - Filter by update date
- `order[createdAt]` - Sort by creation date (asc/desc)
- `page`, `itemsPerPage` - Pagination

**Response:**
```json
{
  "items": [
    {
      "id": "3974d252-b027-46df-9fd8-ddae54bc9ab9",
      "status": "completed",
      "name": "Contract Agreement",
      "emailBody": "Please sign the attached contract.",
      "createdAt": "2024-01-15T10:30:00+01:00",
      "updatedAt": "2024-01-16T14:20:00+01:00",
      "sentAt": "2024-01-15T10:35:00+01:00",
      "completedAt": "2024-01-16T14:20:00+01:00"
    }
  ],
  "count": 127,
  "page": 1,
  "itemsPerPage": 30
}
```

### Get Envelope
```
GET /api/envelopes/{id}
```

### Create Envelope
```
POST /api/envelopes
```

**Request:**
```json
{
  "name": "Contract Agreement",
  "emailBody": "Hello,<br/>Please review and sign the attached document.",
  "emailBodyCompleted": "Thank you for signing. Find your signed documents attached.",
  "senderName": "John Smith",
  "senderEmail": "john@company.com",
  "expiration": 30,
  "signatureType": "simple",
  "authenticationOnOpen": "none",
  "authenticationOnSignature": "none",
  "channelForSigner": "email",
  "properties": {
    "declineAllowed": true,
    "declineReasonRequired": false,
    "sendCompleted": true,
    "generateSignatureSheet": false
  }
}
```

**Response:** Full envelope object with `id`

### Update Envelope
```
PUT /api/envelopes/{id}
```

Same body as create. Only include fields to update.

### Delete Envelope
```
DELETE /api/envelopes/{id}
```

**Response:** 204 No Content

### Send Envelope
```
POST /api/envelopes/{id}/send
```

**Requirements:**
- Status must be `draft`
- At least one signable document
- At least one signer or approver recipient
- `name` and `emailBody` must be set
- All signers must have signature tags on documents
- `validTo` must be in the future (if manually set)

**Response:** Updated envelope with status `sent`

### Cancel Envelope
```
POST /api/envelopes/{id}/cancel
```

**Request (optional):**
```json
{
  "reason": "Document needs revision"
}
```

### Download Documents
```
GET /api/envelopes/{id}/download
```

**Query Parameters:**
| Parameter | Values | Description |
|-----------|--------|-------------|
| `output` | `separate` (default), `combined`, `only_log` | Output format |
| `include_log` | `true`, `false` | Include audit log |
| `document_name_id` | `true`, `false` | Use document ID as filename |

**Response:** Binary file (ZIP or PDF)

### Get Download URL
```
GET /api/envelopes/{id}/download-url
```

**Response:**
```json
{
  "url": "https://...",
  "expiresAt": "2024-01-15T10:35:00+01:00"
}
```
URL valid for 5 minutes.

---

## Files

### Upload File
```
POST /api/files
Content-Type: multipart/form-data
```

**Form Data:**
- `file` - The file to upload (PDF, DOCX, etc.)

**Response:**
```json
{
  "id": "fc5ecf5a-2d91-463a-91cc-c9bc4b11b371",
  "originalName": "contract.pdf",
  "mimeType": "application/pdf",
  "size": 125432,
  "_links": {
    "self": "/api/files/fc5ecf5a-2d91-463a-91cc-c9bc4b11b371"
  }
}
```

---

## Documents

### List Documents
```
GET /api/envelopes/{envelope_id}/documents
```

### Add Document to Envelope
```
POST /api/envelopes/{envelope_id}/documents
```

**Request:**
```json
{
  "file": "/api/files/{file_id}",
  "name": "Contract Agreement",
  "position": 0,
  "signable": true
}
```

### Get Document
```
GET /api/envelopes/{envelope_id}/documents/{document_id}
```

### Update Document
```
PUT /api/envelopes/{envelope_id}/documents/{document_id}
```

### Delete Document
```
DELETE /api/envelopes/{envelope_id}/documents/{document_id}
```

### Download Document
```
GET /api/envelopes/{envelope_id}/documents/{document_id}/download
```

### Get Document Download URL
```
GET /api/envelopes/{envelope_id}/documents/{document_id}/download-url
```

---

## Recipients

### List Recipients
```
GET /api/envelopes/{envelope_id}/recipients
```

### Add Recipient
```
POST /api/envelopes/{envelope_id}/recipients
```

**Request:**
```json
{
  "role": "signer",
  "name": "John Doe",
  "email": "john@example.com",
  "mobile": "+420777666555",
  "signatureType": "simple",
  "authenticationOnOpen": "none",
  "authenticationOnSignature": "sms",
  "channelForSigner": "email",
  "channelForDownload": "email",
  "signingOrder": 1,
  "language": "en",
  "emailBody": "Custom message for this recipient"
}
```

**Role Values:** `signer`, `in_person`, `cc`, `approver`, `autosign`, `semi_autosign`

### Get Recipient
```
GET /api/envelopes/{envelope_id}/recipients/{recipient_id}
```

### Update Recipient
```
PUT /api/envelopes/{envelope_id}/recipients/{recipient_id}
```

### Delete Recipient
```
DELETE /api/envelopes/{envelope_id}/recipients/{recipient_id}
```

### Resend Invitation
```
POST /api/envelopes/{envelope_id}/recipients/{recipient_id}/resend
```

### Trigger Autosign
```
POST /api/envelopes/{envelope_id}/recipients/{recipient_id}/autosign
```
Only for recipients with role `semi_autosign`.

---

## Tags (Signature Fields)

### List Tags
```
GET /api/envelopes/{envelope_id}/tags
```

### Add Tag (by coordinates)
```
POST /api/envelopes/{envelope_id}/tags
```

**Request:**
```json
{
  "document": "/api/envelopes/{envelope_id}/documents/{document_id}",
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "type": "signature",
  "page": 1,
  "xPosition": 100,
  "yPosition": 500,
  "width": 156,
  "height": 60
}
```

### Add Tag (by placeholder)
```
POST /api/envelopes/{envelope_id}/tags
```

**Request:**
```json
{
  "document": "/api/envelopes/{envelope_id}/documents/{document_id}",
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "type": "signature",
  "placeholder": "{{sign_here}}",
  "positioning": "center"
}
```

### Add Tags by Placeholder (all occurrences)
```
POST /api/envelopes/{envelope_id}/tags/by-placeholder
```

**Request:**
```json
{
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "type": "signature",
  "placeholder": "{{sign_here}}",
  "positioning": "center",
  "applyToDocuments": ["document_id_1", "document_id_2"]
}
```

Tags will be created on all occurrences of placeholder across specified documents (or all documents if not specified).

### Get Tag
```
GET /api/envelopes/{envelope_id}/tags/{tag_id}
```

### Update Tag
```
PUT /api/envelopes/{envelope_id}/tags/{tag_id}
```

### Delete Tag
```
DELETE /api/envelopes/{envelope_id}/tags/{tag_id}
```

---

## Webhooks

### List Webhooks
```
GET /api/webhooks
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

**With OAuth:**
```json
{
  "event": "envelopeCompleted",
  "url": "https://your-api.com/webhook",
  "oAuthTokenEndpoint": "https://your-api.com/oauth/token",
  "oAuthClientId": "client_id",
  "oAuthClientSecret": "client_secret",
  "oAuthScopes": ["read"]
}
```

### Get Webhook
```
GET /api/webhooks/{id}
```

**Response includes `secret` for signature verification.**

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

### List Webhook Attempts
```
GET /api/webhooks/{id}/attempts
```

### Resend Webhook Attempt
```
POST /api/webhooks/{webhook_id}/attempts/{attempt_id}/resend
```

---

## Embedding

### Embed Envelope Editing
```
POST /api/envelopes/{id}/embed
```

**Request:**
```json
{
  "target": "edit",
  "allowedActions": ["edit", "send"],
  "language": "en",
  "returnUrl": "https://your-app.com/done",
  "expireAt": "2024-01-15T12:00:00+01:00"
}
```

**Target Values:** `edit`, `send`, `detail`

### Embed Recipient Signing
```
POST /api/envelopes/{envelope_id}/recipients/{recipient_id}/embed
```

**Request:**
```json
{
  "returnUrl": "https://your-app.com/signed",
  "failureUrl": "https://your-app.com/failed",
  "expireAt": "2024-01-15T12:00:00+01:00"
}
```

**Response:**
```json
{
  "url": "https://app.digisign.org/sign/...",
  "expiresAt": "2024-01-15T12:00:00+01:00"
}
```

### Embed Signing Ceremony (Multiple Recipients)
```
POST /api/envelopes/{id}/embed/signing
```

**Request:**
```json
{
  "recipients": ["{recipient_id_1}", "{recipient_id_2}"],
  "returnUrl": "https://your-app.com/done",
  "expireAt": "2024-01-15T12:00:00+01:00"
}
```

### Embed Envelope Detail
```
POST /api/envelopes/{id}/embed/detail
```

**Request:**
```json
{
  "returnUrl": "https://your-app.com/back",
  "language": "en"
}
```

---

## Templates (Generators)

### List Templates
```
GET /api/templates
```

### Get Template
```
GET /api/templates/{id}
```

### Create Envelope from Template
```
POST /api/templates/{id}/generate
```

**Request:**
```json
{
  "name": "Generated Contract",
  "recipients": [
    {
      "templateRecipient": "/api/templates/{id}/recipients/{template_recipient_id}",
      "name": "John Doe",
      "email": "john@example.com"
    }
  ]
}
```

---

## HTTP Status Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (successful delete) |
| 400 | Bad Request - check `violations` |
| 401 | Unauthorized - invalid/expired token |
| 403 | Forbidden - insufficient permissions |
| 404 | Not Found |
| 422 | Validation Error - check `violations` |
| 429 | Rate Limit Exceeded |
| 500 | Server Error |

---

## HATEOAS Navigation

Responses include `_links` and `_actions` for discovery:

```json
{
  "id": "...",
  "status": "draft",
  "_links": {
    "self": "/api/envelopes/3974d252-...",
    "documents": "/api/envelopes/3974d252-.../documents",
    "recipients": "/api/envelopes/3974d252-.../recipients",
    "tags": "/api/envelopes/3974d252-.../tags"
  },
  "_actions": {
    "send": {
      "href": "/api/envelopes/3974d252-.../send",
      "method": "POST"
    },
    "delete": {
      "href": "/api/envelopes/3974d252-...",
      "method": "DELETE"
    }
  }
}
```
