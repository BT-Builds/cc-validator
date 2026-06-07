# Credit Card Validator API

Validates credit card numbers using the Luhn algorithm and identifies card type (Visa, Mastercard, Amex, etc.).

## Endpoints

### POST /validate
Validate a credit card number.

**Request:**
```json
{
  "card_number": "4532015112830366"
}
```

**Response:**
```json
{
  "valid": true,
  "card_type": "Visa",
  "luhn_check": true,
  "message": "Valid Visa card number"
}
```

**cURL:**
```bash
curl -X POST https://cc-validator.vercel.app/validate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: cc-api-key-placeholder" \
  -d '{"card_number": "4532015112830366"}'
```

### POST /detect-type
Detect card type from number pattern.

**Request:**
```json
{
  "card_number": "5500005555555555"
}
```

**Response:**
```json
{
  "card_type": "Mastercard",
  "detected": true
}
```

### GET /health
Health check endpoint (no auth required).

## Supported Card Types
- Visa (13, 16, 19 digits)
- Mastercard (16 digits)
- American Express (15 digits)
- Discover (16 digits)
- Diners Club (14-16 digits)
- JCB (16-19 digits)
- UnionPay (16-19 digits)

## Authentication
Include header `X-API-Key: cc-api-key-placeholder` with all requests.

## Rate Limit
100 requests per minute per IP.

## Postman
[![Run in Postman](https://run.pstmn.io/button.svg)](https://raw.githubusercontent.com/BT-Builds/cc-validator/main/postman_collection.json)
