# Recipients API Reference

Recipients are the people who need to sign, approve, or receive copies of documents.

## Roles

| Role | Description |
|------|-------------|
| `signer` | Signs remotely via email link |
| `in_person` | Signs in person on intermediary's device |
| `cc` | Receives copy of completed documents |
| `approver` | Approves or rejects the envelope |
| `autosign` | Automatic signature (company seal) |
| `semi_autosign` | Triggered automatic signature via API |

## Endpoints

### List Recipients
```
GET /api/envelopes/{envelope}/recipients
```

### Add Recipient
```
POST /api/envelopes/{envelope}/recipients
```

Request body:
```json
{
  "role": "signer",
  "name": "Jan Novak",
  "email": "jan@example.com",
  "mobile": "+420777123456",
  "position": 1,
  "signatureType": "biometric",
  "channelForSigner": "email",
  "channelForDownload": "email",
  "authenticationOnOpen": "none",
  "authenticationOnSignature": "sms",
  "language": "cs"
}
```

### Get Recipient
```
GET /api/envelopes/{envelope}/recipients/{recipient}
```

### Update Recipient
```
PATCH /api/envelopes/{envelope}/recipients/{recipient}
```

### Delete Recipient
```
DELETE /api/envelopes/{envelope}/recipients/{recipient}
```

### Resend Invitation
```
POST /api/envelopes/{envelope}/recipients/{recipient}/resend
```

### Trigger Autosign
```
POST /api/envelopes/{envelope}/recipients/{recipient}/autosign
```

Only for `semi_autosign` role.

## Recipient Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | UUID | Recipient identifier |
| `role` | string | Role (signer, approver, etc.) |
| `name` | string | Display name |
| `email` | string | Email address |
| `mobile` | string | Phone number (E.164 format) |
| `position` | integer | Signing order (lower = earlier) |
| `status` | string | Current status |
| `signatureType` | string | Type of signature |
| `language` | string | UI language code |
| `metadata` | object | Custom data |

## Signature Types

| Type | Description |
|------|-------------|
| `simple` | Simple electronic signature |
| `biometric` | Handwritten signature on touch device |
| `bank_id_sign` | Qualified signature via Bank iD |
| `certificate` | Certificate-based signature |

## Authentication Methods

| Method | Description |
|--------|-------------|
| `none` | No additional authentication |
| `sms` | SMS code verification |
| `bank_id` | Bank iD identity verification |
| `identification` | DigiSign Identify (ID document check) |

### Authentication Points

- `authenticationOnOpen` - When recipient opens the envelope
- `authenticationOnSignature` - When recipient signs

## Delivery Channels

| Channel | Description |
|---------|-------------|
| `email` | Send via email |
| `sms` | Send via SMS |
| `none` | Don't send (for embedded signing) |

### Channel Settings

- `channelForSigner` - How to deliver signing invitation
- `channelForDownload` - How to deliver completed documents
- `channelForNotifications` - How to deliver status updates

## In-Person Signing

For `in_person` role, set `intermediaryEmail` to the DigiSign user who will facilitate the signing:

```json
{
  "role": "in_person",
  "name": "Customer",
  "email": "customer@example.com",
  "intermediaryEmail": "sales@company.com",
  "signatureType": "biometric"
}
```

The intermediary receives an email and can open the signing session on their device.

## Recipient Statuses

| Status | Description |
|--------|-------------|
| `pending` | Waiting to be sent |
| `sent` | Invitation sent |
| `delivered` | Recipient opened the link |
| `signed` | Recipient completed signing |
| `declined` | Recipient declined to sign |
| `disapproved` | Approver rejected |
| `cancelled` | Recipient was cancelled |
| `auth_failed` | Authentication failed 3 times |

## Signature Scenarios

Assign a predefined signature scenario to a recipient:

```json
{
  "role": "signer",
  "name": "Jan Novak",
  "email": "jan@example.com",
  "scenario": "/api/account/signature-scenarios/{scenario_id}"
}
```

List available scenarios:
```
GET /api/account/signature-scenarios
```

## CC Recipient Notifications

For `cc` role, control which notifications they receive:

```json
{
  "role": "cc",
  "name": "Manager",
  "email": "manager@company.com",
  "notificationChannels": {
    "declined": "email",
    "disapproved": "email",
    "expired": "email",
    "authFailed": "none",
    "deliveryFailed": "none"
  }
}
```
