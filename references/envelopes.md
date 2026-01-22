# Envelopes API Reference

An envelope is a container for documents that need to be signed by one or more recipients.

## Lifecycle

```
draft → sent → completed
              → expired
              → declined
              → disapproved
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

**Response:**
```json
{
  "items": [
    {
      "id": "3974d252-b027-46df-9fd8-ddae54bc9ab9",
      "status": "completed",
      "name": "Contract Agreement",
      "emailBody": "Please sign...",
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

**Query Parameters:**

| Parameter | Example | Description |
|-----------|---------|-------------|
| `status[eq]` | `status[eq]=completed` | Filter by exact status |
| `status[neq]` | `status[neq]=draft` | Exclude status |
| `status[in]` | `status[in][]=sent&status[in][]=completed` | Multiple statuses |
| `createdAt[gte]` | `createdAt[gte]=2024-01-01` | Created on or after |
| `createdAt[lte]` | `createdAt[lte]=2024-12-31` | Created on or before |
| `updatedAt[gte]` | `updatedAt[gte]=2024-01-01` | Updated on or after |
| `name[contains]` | `name[contains]=contract` | Name contains string |
| `order[createdAt]` | `order[createdAt]=desc` | Sort by creation date |
| `order[updatedAt]` | `order[updatedAt]=asc` | Sort by update date |
| `page` | `page=2` | Page number (default: 1) |
| `itemsPerPage` | `itemsPerPage=50` | Items per page (default: 30, max: 500) |

### Get Envelope
```
GET /api/envelopes/{id}
```

**Response:** Full envelope object with all attributes, documents, recipients, and tags.

### Create Envelope
```
POST /api/envelopes
```

**Request Body:**
```json
{
  "name": "Contract Agreement",
  "emailBody": "Hello,<br/>Please review and sign the attached contract.",
  "emailBodyCompleted": "Thank you for signing. Here are your signed documents.",
  "senderName": "John Smith",
  "senderEmail": "john@company.com",
  "expiration": 30,
  "validTo": "2024-12-31T23:59:59+01:00",
  "signatureType": "simple",
  "authenticationOnOpen": "none",
  "authenticationOnSignature": "none",
  "authenticationOnDownload": "none",
  "channelForSigner": "email",
  "channelForDownload": "email",
  "timestampDocuments": false,
  "sendCompleted": true,
  "properties": {
    "mergeDocuments": false,
    "mergedDocumentName": "Combined Documents",
    "declineAllowed": true,
    "declineReasonRequired": false,
    "signatureTagParts": ["id", "time", "background"],
    "labelPositioning": "none",
    "sendDocumentsAsEmailAttachment": false,
    "generateSignatureSheet": false,
    "auditLogAvailableToAllRecipients": false,
    "auditLogAvailableToAccountUsers": true,
    "timestampDocuments": false,
    "timestampAuditLog": false,
    "timestampingAuthorities": ["ica_tsa"],
    "sendCompleted": true,
    "discardCompletedAfter": 10950,
    "channelForSender": "email"
  },
  "branding": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "description": "Internal description for this envelope",
  "metadata": "custom-reference-123"
}
```

**Field Reference:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes* | Email subject / envelope name |
| `emailBody` | string | Yes* | Email body to recipients (HTML allowed) |
| `emailBodyCompleted` | string | No | Completion notification email body |
| `senderName` | string | No | Sender display name |
| `senderEmail` | string | No | Sender email (must be verified) |
| `expiration` | integer | No | Days until expiration (default: 30) |
| `validTo` | datetime | No | Explicit expiration date |
| `signatureType` | string | No | Default signature type for recipients |
| `authenticationOnOpen` | string | No | Auth required to view (`none`, `sms`, `bank_id`) |
| `authenticationOnSignature` | string | No | Auth required to sign |
| `authenticationOnDownload` | string | No | Auth required to download |
| `channelForSigner` | string | No | Notification channel (`email`, `sms`) |
| `timestampDocuments` | boolean | No | Add qualified timestamps |
| `sendCompleted` | boolean | No | Send completion notification (default: true) |
| `metadata` | string | No | Custom reference data |
| `description` | string | No | Internal description |
| `branding` | UUID | No | Branding template ID |

*Required before sending

**Signature Types:**
- `simple` - Simple electronic signature
- `biometric` - Handwritten signature capture
- `bank_id_sign` - Bank iD Sign (qualified, Czech)
- `certificate` - Certificate-based signature

**Authentication Methods:**
- `none` - No authentication
- `sms` - SMS code verification
- `bank_id` - Bank iD verification

### Update Envelope
```
PUT /api/envelopes/{id}
```

Same fields as create. Only include fields to update. Only draft envelopes can be updated.

**Note:**
- Omitting a field = don't change it
- Sending `null` = explicitly set to null (may error if not nullable)

### Delete Envelope
```
DELETE /api/envelopes/{id}
```

**Response:** 204 No Content

### Send Envelope
```
POST /api/envelopes/{id}/send
```

**Requirements before sending:**
- Status must be `draft`
- At least one signable document (PDF)
- At least one signer or approver recipient
- `name` and `emailBody` must be set
- All signers must have at least one signature tag
- `validTo` must be in the future (if manually set)

**Response:** Updated envelope with status `sent`

### Cancel Envelope
```
POST /api/envelopes/{id}/cancel
```

**Optional Request Body:**
```json
{
  "reason": "Document needs revision"
}
```

Only sent envelopes can be cancelled.

### Download Documents
```
GET /api/envelopes/{id}/download
```

**Query Parameters:**

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `output` | `separate`, `combined`, `only_log` | `separate` | Output format |
| `include_log` | `true`, `false` | `false` | Include audit log |
| `document_name_id` | `true`, `false` | `false` | Use document ID as filename |

**Output Formats:**
- `separate` - ZIP file with all documents separately
- `combined` - All PDF documents merged into one file
- `only_log` - Only the audit log PDF

**Response:** Binary file (ZIP or PDF) with appropriate Content-Type header.

### Get Download URL
```
GET /api/envelopes/{id}/download-url
```

**Query Parameters:** Same as `/download`

**Response:**
```json
{
  "url": "https://storage.digisign.org/...",
  "expiresAt": "2024-01-15T10:40:00+01:00"
}
```

URL valid for 5 minutes.

## Envelope Properties

The `properties` object contains envelope-level settings:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `mergeDocuments` | boolean | false | Merge all documents into one PDF |
| `mergedDocumentName` | string | - | Name for merged document |
| `declineAllowed` | boolean | true | Allow signers to decline |
| `declineReasonRequired` | boolean | false | Require reason when declining |
| `signatureTagParts` | array | ["id","time","background"] | Parts shown in signature |
| `labelPositioning` | string | "none" | Signature label position |
| `sendDocumentsAsEmailAttachment` | boolean | false | Attach docs to emails |
| `generateSignatureSheet` | boolean | false | Generate signature sheet |
| `auditLogAvailableToAllRecipients` | boolean | false | Share audit log with all |
| `auditLogAvailableToAccountUsers` | boolean | true | Share audit log with account |
| `timestampDocuments` | boolean | false | Add qualified timestamps |
| `timestampAuditLog` | boolean | false | Timestamp the audit log |
| `timestampingAuthorities` | array | ["ica_tsa"] | TSA providers |
| `sendCompleted` | boolean | true | Send completion notifications |
| `discardCompletedAfter` | integer | 10950 | Days to keep after completion |
| `channelForSender` | string | "email" | Sender notification channel |

**Signature Tag Parts:**
- `id` - Signer identifier
- `time` - Signature timestamp
- `background` - Background image
- `name` - Signer name
- `reason` - Signing reason

**Label Positioning:**
- `none` - No label
- `top_left`, `top_right`, `bottom_left`, `bottom_right` - Corner positions

## Email Body HTML

Allowed HTML tags in `emailBody` and `emailBodyCompleted`:
- `a[href|title]` - Links
- `br` - Line breaks
- `u`, `em`, `strong`, `i`, `b` - Text formatting
- `ul`, `ol`, `li` - Lists

If no HTML tags are present, newlines (`\n`) are converted to `<br>`.

## HATEOAS Navigation

Responses include `_links` and `_actions` for API navigation:

```json
{
  "id": "3974d252-b027-46df-9fd8-ddae54bc9ab9",
  "status": "draft",
  "_links": {
    "self": "/api/envelopes/3974d252-b027-46df-9fd8-ddae54bc9ab9",
    "documents": "/api/envelopes/3974d252-b027-46df-9fd8-ddae54bc9ab9/documents",
    "recipients": "/api/envelopes/3974d252-b027-46df-9fd8-ddae54bc9ab9/recipients",
    "tags": "/api/envelopes/3974d252-b027-46df-9fd8-ddae54bc9ab9/tags"
  },
  "_actions": {
    "send": {
      "href": "/api/envelopes/3974d252-b027-46df-9fd8-ddae54bc9ab9/send",
      "method": "POST"
    },
    "delete": {
      "href": "/api/envelopes/3974d252-b027-46df-9fd8-ddae54bc9ab9",
      "method": "DELETE"
    }
  }
}
```

## Example: Complete Envelope Creation Flow

```javascript
// 1. Create envelope
const envelope = await client.request('POST', '/api/envelopes', {
  name: 'Employment Contract',
  emailBody: 'Please review and sign your employment contract.',
  expiration: 14,
  signatureType: 'simple',
  properties: {
    declineAllowed: true,
    sendCompleted: true
  }
});

// 2. Upload and add document
const file = await client.uploadFile('contract.pdf');
await client.request('POST', `/api/envelopes/${envelope.id}/documents`, {
  file: `/api/files/${file.id}`,
  name: 'Employment Contract'
});

// 3. Add recipient
const recipient = await client.request('POST', `/api/envelopes/${envelope.id}/recipients`, {
  role: 'signer',
  name: 'Jane Smith',
  email: 'jane@example.com',
  signatureType: 'simple'
});

// 4. Add signature tag
await client.request('POST', `/api/envelopes/${envelope.id}/tags/by-placeholder`, {
  recipient: `/api/envelopes/${envelope.id}/recipients/${recipient.id}`,
  type: 'signature',
  placeholder: '{{employee_signature}}',
  positioning: 'center'
});

// 5. Send envelope
await client.request('POST', `/api/envelopes/${envelope.id}/send`);
```

## Notifications Control

| Setting | Location | Description |
|---------|----------|-------------|
| `channelForSender` | properties | Sender notifications (`email`, `none`) |
| `channelForSigner` | envelope/recipient | Signer notifications |
| `channelForDownload` | envelope/recipient | Download notifications |
| `sendCompleted` | properties | Send completion emails |

Set `channelForSender: "none"` in properties to disable all sender notifications.
