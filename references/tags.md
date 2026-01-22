# Tags API Reference

Tags define where recipients sign, approve, or fill in information on documents.

## Tag Types

| Type | Description | Size |
|------|-------------|------|
| `signature` | Signature field | 55x21mm |
| `approval` | Approval stamp | 55x21mm |
| `text` | Text input field | Configurable |
| `document` | ID document photos | Configurable |
| `attachment` | File attachment | Configurable |
| `checkbox` | Checkbox | Configurable |
| `radio_button` | Radio button | Configurable |
| `date_of_signature` | Auto-filled date | Configurable |

## Endpoints

### List Tags
```
GET /api/envelopes/{envelope}/tags
```

### Add Tag
```
POST /api/envelopes/{envelope}/tags
```

### Add Tags by Placeholder
```
POST /api/envelopes/{envelope}/tags/by-placeholder
```

Finds all occurrences of placeholder text and adds tags.

### Get Tag
```
GET /api/envelopes/{envelope}/tags/{tag}
```

### Update Tag
```
PATCH /api/envelopes/{envelope}/tags/{tag}
```

### Delete Tag
```
DELETE /api/envelopes/{envelope}/tags/{tag}
```

## Positioning Methods

### By Placeholder (Recommended)

Use text in the PDF as an anchor point:

```json
{
  "document": "/api/envelopes/{env}/documents/{doc}",
  "recipient": "/api/envelopes/{env}/recipients/{rec}",
  "type": "signature",
  "placeholder": "{{podpis_klienta}}",
  "positioning": "top_left"
}
```

**Placeholder rules:**
- Only ASCII letters, numbers, hyphens, underscores, brackets
- Regex: `^[\w\-\{\}\[\]\(\)=\,\`]*$`
- Can use white text on white background to hide it

**Positioning options:**

| Value | Description |
|-------|-------------|
| `top_left` | Tag's top-left corner at placeholder's top-left |
| `top_center` | Tag's top-center at placeholder's top-center |
| `top_right` | Tag's top-right at placeholder's top-right |
| `middle_left` | Tag's middle-left at placeholder's middle-left |
| `center` | Tag's center at placeholder's center |
| `middle_right` | Tag's middle-right at placeholder's middle-right |
| `bottom_left` | Tag's bottom-left at placeholder's bottom-left |
| `bottom_center` | Tag's bottom-center at placeholder's bottom-center |
| `bottom_right` | Tag's bottom-right at placeholder's bottom-right |

### By Coordinates

Specify exact position on page:

```json
{
  "document": "/api/envelopes/{env}/documents/{doc}",
  "recipient": "/api/envelopes/{env}/recipients/{rec}",
  "type": "signature",
  "page": 1,
  "xPosition": 100,
  "yPosition": 500
}
```

**Coordinate system:**
- Units: points (72 points = 1 inch)
- Origin: top-left corner of page
- `xPosition`: horizontal offset from left
- `yPosition`: vertical offset from top

## Tag Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | UUID | Tag identifier |
| `type` | string | Tag type |
| `document` | IRI | Document reference |
| `recipient` | IRI | Recipient reference |
| `page` | integer | Page number (1-indexed) |
| `xPosition` | float | X coordinate (points) |
| `yPosition` | float | Y coordinate (points) |
| `width` | float | Tag width |
| `height` | float | Tag height |
| `required` | boolean | Is field required |
| `label` | string | Field label |
| `placeholder` | string | Placeholder text used |
| `positioning` | string | Positioning relative to placeholder |

## Multiple Occurrences

Use `/tags/by-placeholder` to place tags on all occurrences:

```json
{
  "recipient": "/api/envelopes/{env}/recipients/{rec}",
  "type": "signature",
  "placeholder": "{{sign}}",
  "positioning": "center"
}
```

To limit to specific documents:

```json
{
  "recipient": "/api/envelopes/{env}/recipients/{rec}",
  "type": "signature",
  "placeholder": "{{sign}}",
  "positioning": "center",
  "applyToDocuments": ["doc-id-1", "doc-id-2"]
}
```

## Checkbox and Radio Buttons

### Checkbox
```json
{
  "type": "checkbox",
  "document": "/api/envelopes/{env}/documents/{doc}",
  "recipient": "/api/envelopes/{env}/recipients/{rec}",
  "page": 1,
  "xPosition": 50,
  "yPosition": 300,
  "required": true,
  "label": "I agree to terms"
}
```

### Radio Button Group
```json
{
  "type": "radio_button",
  "document": "/api/envelopes/{env}/documents/{doc}",
  "recipient": "/api/envelopes/{env}/recipients/{rec}",
  "page": 1,
  "xPosition": 50,
  "yPosition": 300,
  "group": "payment_method",
  "label": "Credit Card"
}
```

Multiple radio buttons with the same `group` form a selection group.

## Text Fields

```json
{
  "type": "text",
  "document": "/api/envelopes/{env}/documents/{doc}",
  "recipient": "/api/envelopes/{env}/recipients/{rec}",
  "placeholder": "{{customer_name}}",
  "positioning": "top_left",
  "required": true,
  "label": "Full Name",
  "width": 200,
  "height": 20
}
```

## Requirements

- Signature tags are **required** for signers (`signer`, `in_person`, `autosign`, `semi_autosign`)
- Approval tags are optional for approvers
- Tags can only be added to PDF documents
- Tag must be placed on a signable document
