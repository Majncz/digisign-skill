# Recipients API Reference

Recipients are the people who need to sign, approve, or receive copies of documents in an envelope.

## Roles

| Role | Description |
|------|-------------|
| `signer` | Remote signer - receives email with signing link, signs on their own device |
| `in_person` | In-person signer - signs on intermediary's device (tablet/phone) |
| `cc` | Copy recipient - receives completed documents, cannot sign |
| `approver` | Approver - can approve or reject the envelope |
| `autosign` | Auto-signer - automatically signs when their turn comes (requires company seal) |
| `semi_autosign` | Semi-auto signer - signs when triggered via API call |

## Endpoints

### List Recipients
```
GET /api/envelopes/{envelope_id}/recipients
```

**Response:**
```json
{
  "items": [
    {
      "id": "9ab9d252-b027-46df-9fd8-ddae54bc3974",
      "role": "signer",
      "status": "signed",
      "name": "John Doe",
      "email": "john@example.com",
      "mobile": "+420777666555",
      "signatureType": "simple",
      "signingOrder": 1,
      "signedAt": "2024-01-16T14:20:00+01:00"
    }
  ],
  "count": 2,
  "page": 1,
  "itemsPerPage": 30
}
```

### Add Recipient
```
POST /api/envelopes/{envelope_id}/recipients
```

**Request Body:**
```json
{
  "role": "signer",
  "name": "Jan Novak",
  "email": "jan@example.com",
  "mobile": "+420777123456",
  "company": "Example Corp",
  "function": "CEO",
  "contractingParty": "Buyer",
  "birthdate": "1980-05-15",
  "birthnumber": "8005150123",
  "identificationNumber": "12345678",
  "address": "Vaclavske namesti 1, Praha",
  "signingOrder": 1,
  "signatureType": "simple",
  "authenticationOnOpen": "none",
  "authenticationOnSignature": "sms",
  "authenticationOnDownload": "none",
  "channelForSigner": "email",
  "channelForDownload": "email",
  "language": "cs",
  "emailBody": "Custom message for this recipient",
  "emailBodyCompleted": "Custom completion message",
  "scenario": "/api/account/signature-scenarios/{scenario_id}",
  "identifyScenario": "/api/account/identify-scenarios/{identify_scenario_id}",
  "bankIdScopes": ["profile.name", "profile.birthdate"],
  "delegation": false,
  "approvalMode": "per_envelope",
  "approveDocumentsAtOnce": false,
  "signDocumentsAtOnce": false,
  "notificationChannels": {
    "declined": "email",
    "disapproved": "email",
    "expired": "email",
    "authFailed": "email",
    "deliveryFailed": "email",
    "identificationDenied": "email",
    "deleted": null,
    "cancelled": "email",
    "afterSent": null,
    "envelopeNotification": null
  },
  "notificationCopies": ["manager@example.com"],
  "autoplacementTagPlaceholder": "{{sign_jan}}",
  "autoplacementTagPositioning": "center",
  "autoplacementTagSize": 20,
  "visibleFields": ["name", "email", "company"],
  "validatedFields": ["name", "email"],
  "identifyValidatedFields": ["name", "birthdate"],
  "metadata": ""
}
```

**Field Reference:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | string | Yes | Recipient role |
| `name` | string | Yes | Display name |
| `email` | string | Yes* | Email address |
| `mobile` | string | No | Phone number (E.164: +420777666555) |
| `company` | string | No | Company name |
| `function` | string | No | Job title/function |
| `contractingParty` | string | No | Party in contract (e.g., "Buyer", "Seller") |
| `birthdate` | date | No | Date of birth (YYYY-MM-DD) |
| `birthnumber` | string | No | Czech birth number (rodne cislo) |
| `identificationNumber` | string | No | Czech ICO |
| `address` | string | No | Address |
| `signingOrder` | integer | No | Signing order (1 = first, default: 1) |
| `signatureType` | string | No | Signature type |
| `authenticationOnOpen` | string | No | Auth to view document |
| `authenticationOnSignature` | string | No | Auth to sign |
| `authenticationOnDownload` | string | No | Auth to download |
| `channelForSigner` | string | No | How to send signing invitation |
| `channelForDownload` | string | No | How to send completed docs |
| `language` | string | No | UI language (cs, en, sk, pl) |
| `emailBody` | string | No | Custom email body for this recipient |
| `scenario` | IRI | No | Signature scenario reference |
| `delegation` | boolean | No | Allow recipient to delegate (default: false) |
| `metadata` | string | No | Custom reference data |

*Email required for `signer`, `cc`, `approver` roles

### Get Recipient
```
GET /api/envelopes/{envelope_id}/recipients/{recipient_id}
```

### Update Recipient
```
PUT /api/envelopes/{envelope_id}/recipients/{recipient_id}
```

Same fields as create. Only draft envelopes can have recipients updated.

### Delete Recipient
```
DELETE /api/envelopes/{envelope_id}/recipients/{recipient_id}
```

### Resend Invitation
```
POST /api/envelopes/{envelope_id}/recipients/{recipient_id}/resend
```

Resends the signing invitation email/SMS. Only for sent envelopes with recipients who haven't signed yet.

### Trigger Autosign
```
POST /api/envelopes/{envelope_id}/recipients/{recipient_id}/autosign
```

Triggers automatic signature for `semi_autosign` recipients. Requires:
- Recipient role must be `semi_autosign`
- It's the recipient's turn in signing order
- Company seal must be configured

## Recipient Statuses

| Status | Description |
|--------|-------------|
| `draft` | Not yet sent (envelope is draft) |
| `sent` | Invitation sent, waiting for action |
| `delivered` | Recipient opened the signing link |
| `signed` | Recipient completed signing |
| `declined` | Recipient declined to sign |
| `disapproved` | Approver rejected the envelope |
| `cancelled` | Recipient was cancelled |
| `authFailed` | Authentication failed 3 times |

## Signature Types

| Type | Description | Requirements |
|------|-------------|--------------|
| `simple` | Simple electronic signature | None |
| `biometric` | Handwritten signature capture | Touch device |
| `bank_id_sign` | Qualified signature via Bank iD | Bank iD account |
| `certificate` | Certificate-based signature | Personal certificate |

## Authentication Methods

| Method | Description |
|--------|-------------|
| `none` | No additional authentication |
| `sms` | SMS code verification (requires `mobile`) |
| `bank_id` | Bank iD identity verification |

### Authentication Points

| Setting | When Applied |
|---------|--------------|
| `authenticationOnOpen` | When recipient first opens the envelope |
| `authenticationOnSignature` | When recipient clicks to sign |
| `authenticationOnDownload` | When recipient downloads completed documents |

## Delivery Channels

| Channel | Description |
|---------|-------------|
| `email` | Send via email |
| `sms` | Send via SMS |
| `none` | Don't send (for embedded signing) |

### Channel Settings

| Setting | Description |
|---------|-------------|
| `channelForSigner` | How to deliver signing invitation |
| `channelForDownload` | How to deliver completed documents |

## Signing Order

Control the order in which recipients receive their invitations:

```json
{
  "recipients": [
    { "name": "John", "signingOrder": 1 },  // Signs first
    { "name": "Jane", "signingOrder": 2 },  // Signs after John
    { "name": "Bob", "signingOrder": 2 }    // Signs parallel with Jane
  ]
}
```

- Lower number = earlier in sequence
- Same number = sign in parallel
- Default is 1 (all parallel)

## In-Person Signing

For `in_person` role, an intermediary facilitates the signing:

```json
{
  "role": "in_person",
  "name": "Customer Name",
  "email": "customer@example.com",
  "intermediaryName": "Sales Rep",
  "intermediaryEmail": "sales@company.com",
  "signatureType": "biometric"
}
```

The intermediary receives an email and opens the signing session on their device (tablet/phone). The signer signs in person.

## Auto-Sign Recipients

### `autosign` Role
Automatically signs when it's their turn:
- Requires company seal to be configured
- Must use `signatureType: "simple"`
- No authentication allowed (`authenticationOnSignature: "none"`)

### `semi_autosign` Role
Signs when triggered via API:
```
POST /api/envelopes/{envelope_id}/recipients/{recipient_id}/autosign
```

Useful for automated workflows where you control when the signature is applied.

## Bank iD Integration

### Bank iD Authentication
Verify signer identity via Czech banking identity:

```json
{
  "role": "signer",
  "name": "Jan Novak",
  "email": "jan@example.com",
  "authenticationOnSignature": "bank_id",
  "bankIdScopes": ["profile.name", "profile.birthdate", "profile.birthnumber"]
}
```

**Available Bank iD Scopes:**
- `profile.name` - Full name
- `profile.birthdate` - Date of birth
- `profile.birthnumber` - Czech birth number
- `profile.addresses` - Addresses
- `profile.idcards` - ID card info
- `profile.paymentAccounts` - Bank account info

### Bank iD Sign
Qualified electronic signature via Bank iD:

```json
{
  "role": "signer",
  "name": "Jan Novak",
  "email": "jan@example.com",
  "signatureType": "bank_id_sign"
}
```

## Signature Scenarios

Pre-configured signature settings:

```json
{
  "role": "signer",
  "name": "Jan Novak",
  "email": "jan@example.com",
  "scenario": "/api/account/signature-scenarios/{scenario_id}"
}
```

**List available scenarios:**
```
GET /api/account/signature-scenarios
```

Scenarios can pre-configure:
- Signature type
- Authentication methods
- Bank iD scopes
- UI customizations

## Identity Verification (DigiSign Identify)

Verify identity via ID document:

```json
{
  "role": "signer",
  "name": "Jan Novak",
  "email": "jan@example.com",
  "identifyScenario": "/api/account/identify-scenarios/{identify_scenario_id}",
  "identifyValidatedFields": ["name", "birthdate"]
}
```

The recipient must verify their identity by photographing their ID document before signing.

## Notification Control

### Notification Channels by Event

```json
{
  "notificationChannels": {
    "declined": "email",        // When envelope is declined
    "disapproved": "email",     // When envelope is disapproved
    "expired": "email",         // When envelope expires
    "authFailed": "email",      // When auth fails
    "deliveryFailed": "email",  // When delivery fails
    "identificationDenied": null, // When ID verification fails
    "deleted": null,            // When envelope is deleted
    "cancelled": "email",       // When envelope is cancelled
    "afterSent": null,          // After envelope is sent
    "envelopeNotification": null // General notifications
  }
}
```

Values: `"email"`, `"sms"`, or `null` (disabled)

### Notification Copies

Send copies of notifications to additional addresses:

```json
{
  "notificationCopies": ["manager@example.com", "hr@example.com"]
}
```

## Approval Mode

For `approver` role:

| Mode | Description |
|------|-------------|
| `per_envelope` | One approval for entire envelope |
| `per_document` | Separate approval for each document |

```json
{
  "role": "approver",
  "approvalMode": "per_document",
  "approveDocumentsAtOnce": false
}
```

## Visible and Validated Fields

Control which recipient fields are visible and validated during signing:

```json
{
  "visibleFields": ["name", "email", "company", "function"],
  "validatedFields": ["name", "email"]
}
```

Validated fields are checked against what the recipient entered.

## Response Example

```json
{
  "id": "9ab9d252-b027-46df-9fd8-ddae54bc3974",
  "status": "sent",
  "role": "signer",
  "name": "Jan Novak",
  "email": "jan@example.com",
  "mobile": "+420777123456",
  "company": "Example Corp",
  "signatureType": "simple",
  "signingOrder": 1,
  "language": "cs",
  "sentAt": "2024-01-15T10:35:00+01:00",
  "deliveredAt": null,
  "signedAt": null,
  "createdAt": "2024-01-15T10:30:00+01:00",
  "updatedAt": "2024-01-15T10:35:00+01:00",
  "_links": {
    "self": "/api/envelopes/.../recipients/9ab9d252-...",
    "embed": "/api/envelopes/.../recipients/9ab9d252-.../embed"
  }
}
```
