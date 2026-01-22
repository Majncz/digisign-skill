# Tags API Reference

Tags define where recipients sign, approve, or fill in information on documents. Every signer must have at least one signature tag before an envelope can be sent.

## Tag Types

| Type | Description | Default Size |
|------|-------------|--------------|
| `signature` | Signature field | 55x21mm (156x60 points) |
| `approval` | Approval stamp | 55x21mm (156x60 points) |
| `text` | Text input field | Configurable |
| `document` | ID document photos | Configurable |
| `attachment` | File attachment | Configurable |
| `checkbox` | Checkbox | Configurable |
| `radio_button` | Radio button | Configurable |
| `date_of_signature` | Auto-filled signature date | Configurable |

## Endpoints

### List Tags
```
GET /api/envelopes/{envelope_id}/tags
```

**Response:**
```json
{
  "items": [
    {
      "id": "7a8b9c0d-1234-5678-abcd-ef0123456789",
      "type": "signature",
      "page": 1,
      "xPosition": 100,
      "yPosition": 500,
      "width": 156,
      "height": 60,
      "required": true,
      "document": "/api/envelopes/.../documents/...",
      "recipient": "/api/envelopes/.../recipients/..."
    }
  ],
  "count": 2,
  "page": 1,
  "itemsPerPage": 30
}
```

### Add Tag (Single)
```
POST /api/envelopes/{envelope_id}/tags
```

**By Coordinates:**
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

**By Placeholder:**
```json
{
  "document": "/api/envelopes/{envelope_id}/documents/{document_id}",
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "type": "signature",
  "placeholder": "{{sign_here}}",
  "positioning": "center"
}
```

### Add Tags by Placeholder (Multiple)
```
POST /api/envelopes/{envelope_id}/tags/by-placeholder
```

Creates tags on ALL occurrences of the placeholder across documents.

**Request:**
```json
{
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "type": "signature",
  "placeholder": "{{sign_here}}",
  "positioning": "center"
}
```

**Limit to specific documents:**
```json
{
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "type": "signature",
  "placeholder": "{{sign_here}}",
  "positioning": "center",
  "applyToDocuments": ["document_id_1", "document_id_2"]
}
```

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

## Positioning Methods

### By Placeholder (Recommended)

Use text in the PDF as an anchor point. DigiSign finds the placeholder text and positions the tag relative to it.

```json
{
  "document": "/api/envelopes/{envelope_id}/documents/{document_id}",
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "type": "signature",
  "placeholder": "{{podpis_klienta}}",
  "positioning": "center"
}
```

**Placeholder Rules:**
- Only ASCII letters, numbers, and these special characters: `- _ { } [ ] ( ) = , \``
- Regex pattern: `^[\w\-\{\}\[\]\(\)=\,\`]*$`
- Can use white text on white background to make it invisible
- If placeholder not found, API returns validation error

**Positioning Values:**

| Value | Description |
|-------|-------------|
| `top_left` | Tag's top-left corner aligns with placeholder's top-left |
| `top_center` | Tag's top-center aligns with placeholder's top-center |
| `top_right` | Tag's top-right corner aligns with placeholder's top-right |
| `middle_left` | Tag's middle-left aligns with placeholder's middle-left |
| `center` | Tag's center aligns with placeholder's center |
| `middle_right` | Tag's middle-right aligns with placeholder's middle-right |
| `bottom_left` | Tag's bottom-left corner aligns with placeholder's bottom-left |
| `bottom_center` | Tag's bottom-center aligns with placeholder's bottom-center |
| `bottom_right` | Tag's bottom-right corner aligns with placeholder's bottom-right |

### By Coordinates

Specify exact position on page using points (72 points = 1 inch).

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

**Coordinate System:**
- Units: points (72 points = 1 inch, ~2.83 points = 1mm)
- Origin: **top-left corner** of page (unlike PDF default which is bottom-left)
- `page`: Page number, **1-indexed** (first page = 1)
- `xPosition`: Horizontal offset from left edge
- `yPosition`: Vertical offset from top edge

**Common Page Sizes (in points):**
- A4: 595 x 842
- Letter: 612 x 792

**Example positions for A4:**
```
Top-left corner: xPosition=50, yPosition=50
Top-right corner: xPosition=545, yPosition=50
Bottom-left corner: xPosition=50, yPosition=792
Center: xPosition=297, yPosition=421
```

## Tag Attributes

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | Tag type (signature, text, etc.) |
| `document` | IRI | Yes* | Document reference |
| `recipient` | IRI | Yes | Recipient reference |
| `page` | integer | No** | Page number (1-indexed) |
| `xPosition` | float | No** | X coordinate in points |
| `yPosition` | float | No** | Y coordinate in points |
| `placeholder` | string | No** | Placeholder text to find |
| `positioning` | string | No | Position relative to placeholder |
| `width` | float | No | Tag width in points |
| `height` | float | No | Tag height in points |
| `required` | boolean | No | Is field required (default: true for signature) |
| `label` | string | No | Field label displayed to user |
| `group` | string | No | Group name for radio buttons |
| `value` | string | No | Pre-filled value for text fields |

*Not required for `/tags/by-placeholder` endpoint
**Either coordinates (page, xPosition, yPosition) OR placeholder required

## Signature Tags

Required for all signing recipients (`signer`, `in_person`, `autosign`, `semi_autosign`).

```json
{
  "document": "/api/envelopes/{envelope_id}/documents/{document_id}",
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "type": "signature",
  "placeholder": "{{employee_signature}}",
  "positioning": "center"
}
```

**Signature Tag Dimensions:**
- Default: 55mm x 21mm (156 x 60 points)
- Customizable via `width` and `height`

## Approval Tags

For `approver` recipients. Approval tags are optional but recommended.

```json
{
  "document": "/api/envelopes/{envelope_id}/documents/{document_id}",
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "type": "approval",
  "placeholder": "{{manager_approval}}",
  "positioning": "center"
}
```

## Text Fields

Collect text input from recipients.

```json
{
  "document": "/api/envelopes/{envelope_id}/documents/{document_id}",
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "type": "text",
  "placeholder": "{{customer_name}}",
  "positioning": "top_left",
  "required": true,
  "label": "Full Name",
  "width": 200,
  "height": 20,
  "value": "Pre-filled value"
}
```

**Text Field Options:**
| Option | Type | Description |
|--------|------|-------------|
| `label` | string | Label shown above field |
| `required` | boolean | Must be filled before signing |
| `value` | string | Pre-filled value |
| `width` | float | Field width in points |
| `height` | float | Field height in points |
| `maxLength` | integer | Maximum character length |

## Checkbox Fields

```json
{
  "document": "/api/envelopes/{envelope_id}/documents/{document_id}",
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "type": "checkbox",
  "page": 1,
  "xPosition": 50,
  "yPosition": 300,
  "required": true,
  "label": "I agree to the terms and conditions",
  "checked": false
}
```

**Checkbox Options:**
| Option | Type | Description |
|--------|------|-------------|
| `label` | string | Text next to checkbox |
| `required` | boolean | Must be checked before signing |
| `checked` | boolean | Pre-checked state |

## Radio Button Groups

Multiple radio buttons with the same `group` form a selection where only one can be selected.

```json
// Option 1
{
  "type": "radio_button",
  "document": "/api/envelopes/{envelope_id}/documents/{document_id}",
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "page": 1,
  "xPosition": 50,
  "yPosition": 300,
  "group": "payment_method",
  "label": "Credit Card",
  "value": "credit_card"
}

// Option 2
{
  "type": "radio_button",
  "document": "/api/envelopes/{envelope_id}/documents/{document_id}",
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "page": 1,
  "xPosition": 50,
  "yPosition": 320,
  "group": "payment_method",
  "label": "Bank Transfer",
  "value": "bank_transfer"
}
```

## Date of Signature

Automatically filled with the signature date.

```json
{
  "document": "/api/envelopes/{envelope_id}/documents/{document_id}",
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "type": "date_of_signature",
  "placeholder": "{{signature_date}}",
  "positioning": "top_left",
  "format": "DD.MM.YYYY"
}
```

## Document Upload Tag

For recipients to upload ID document photos.

```json
{
  "document": "/api/envelopes/{envelope_id}/documents/{document_id}",
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "type": "document",
  "placeholder": "{{id_photo}}",
  "positioning": "center",
  "required": true
}
```

## Attachment Tag

For recipients to upload additional files.

```json
{
  "document": "/api/envelopes/{envelope_id}/documents/{document_id}",
  "recipient": "/api/envelopes/{envelope_id}/recipients/{recipient_id}",
  "type": "attachment",
  "placeholder": "{{attachment}}",
  "positioning": "center",
  "required": false,
  "label": "Upload supporting documents"
}
```

## Requirements and Validation

1. **Signature tags are required** for signing recipients (`signer`, `in_person`, `autosign`, `semi_autosign`)
2. Tags can only be added to **PDF documents** (documents with `signable: true`)
3. Envelope cannot be sent without signature tags for all signers
4. Placeholder must exist in document or API returns error:
   ```json
   {
     "violations": [{
       "propertyPath": "placeholder",
       "message": "Placeholder '{{sign_here}}' not found in document"
     }]
   }
   ```

## Recipient Auto-Placement

Instead of manually adding tags, use recipient's auto-placement settings:

```json
// When adding recipient
{
  "role": "signer",
  "name": "John Doe",
  "email": "john@example.com",
  "autoplacementTagPlaceholder": "{{john_signature}}",
  "autoplacementTagPositioning": "center",
  "autoplacementTagSize": 20
}
```

This automatically creates signature tags at all occurrences of `{{john_signature}}` in all documents.

## Response Example

```json
{
  "id": "7a8b9c0d-1234-5678-abcd-ef0123456789",
  "type": "signature",
  "page": 2,
  "xPosition": 100.5,
  "yPosition": 500.25,
  "width": 156,
  "height": 60,
  "required": true,
  "placeholder": "{{sign_here}}",
  "positioning": "center",
  "document": "/api/envelopes/.../documents/...",
  "recipient": "/api/envelopes/.../recipients/...",
  "createdAt": "2024-01-15T10:30:00+01:00",
  "updatedAt": "2024-01-15T10:30:00+01:00",
  "_links": {
    "self": "/api/envelopes/.../tags/7a8b9c0d-..."
  }
}
```
