# Envelopes API Reference

An envelope is a container for documents that need to be signed by one or more recipients.

## Lifecycle

```
draft → sent → completed
              → expired
              → declined
              → cancelled
```

## Statuses

| Status | Description |
|--------|-------------|
| `draft` | Envelope is being prepared, not yet sent |
| `sent` | Envelope has been sent to recipients |
| `completed` | All recipients have signed/approved |
| `expired` | Expiration date passed before completion |
| `declined` | A signer declined to sign |
| `disapproved` | An approver rejected the envelope |
| `cancelled` | Sender cancelled the envelope |

## Endpoints

### List Envelopes
```
GET /api/envelopes
```

Query parameters:
- `status` - Filter by status
- `updatedAt[after]` - Filter by update date
- `page` - Page number

### Get Envelope
```
GET /api/envelopes/{id}
```

### Create Envelope
```
POST /api/envelopes
```

Request body:
```json
{
  "name": "Contract Agreement",
  "emailBody": "Please sign the attached documents.",
  "emailBodyCompleted": "Here are your signed documents.",
  "senderName": "John Smith",
  "senderEmail": "john@company.com",
  "expiresAt": "2024-12-31T23:59:59+01:00",
  "metadata": {
    "customField": "value"
  }
}
```

### Update Envelope
```
PATCH /api/envelopes/{id}
```

Only draft envelopes can be updated.

### Delete Envelope
```
DELETE /api/envelopes/{id}
```

### Send Envelope
```
POST /api/envelopes/{id}/send
```

Requirements:
- Status must be `draft`
- At least one signable document (PDF)
- At least one signer or approver recipient
- `name` and `emailBody` must be set
- All signers must have signature tags

### Cancel Envelope
```
POST /api/envelopes/{id}/cancel
```

Only sent envelopes can be cancelled.

### Download Documents
```
GET /api/envelopes/{id}/download
```

Query parameters:
- `output`: `separate` (ZIP), `combined` (merged PDF), `only_log` (audit log only)
- `include_log`: `true`/`false` - include audit log
- `document_name_id`: `true`/`false` - use document ID as filename

### Get Download URL
```
GET /api/envelopes/{id}/download-url
```

Returns a pre-signed URL valid for 5 minutes.

## Envelope Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | UUID | Envelope identifier |
| `name` | string | Email subject / envelope name |
| `status` | string | Current status |
| `emailBody` | string | Email body (HTML allowed) |
| `emailBodyCompleted` | string | Completion email body |
| `senderName` | string | Sender display name |
| `senderEmail` | string | Sender email address |
| `expiresAt` | datetime | Expiration date |
| `metadata` | object | Custom key-value data |
| `createdAt` | datetime | Creation timestamp |
| `updatedAt` | datetime | Last update timestamp |
| `sentAt` | datetime | When envelope was sent |
| `completedAt` | datetime | When envelope was completed |

## Email Body HTML

Allowed HTML tags in `emailBody`:
- `a[href|title]`
- `br`
- `u`, `em`, `strong`, `i`, `b`
- `ul`, `ol`, `li`

If no HTML tags are present, newlines (`\n`) are converted to `<br>`.

## HATEOAS Links

Responses include `_links` and `_actions` for navigating related resources:

```json
{
  "id": "abc-123",
  "_links": {
    "self": "/api/envelopes/abc-123",
    "documents": "/api/envelopes/abc-123/documents",
    "recipients": "/api/envelopes/abc-123/recipients"
  },
  "_actions": {
    "send": "/api/envelopes/abc-123/send"
  }
}
```

## Notifications Control

| Attribute | Description |
|-----------|-------------|
| `channelForSender` | `email` or `none` - notifications to sender |

Set `channelForSender: "none"` on the envelope to disable all sender notifications.
