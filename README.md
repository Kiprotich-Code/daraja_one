# Daraja One - M-Pesa C2B Callback Handler

A Django REST Framework application that handles Safaricom Daraja M-Pesa C2B (Customer to Business) payment callbacks with Google Sheets integration for account validation and Apps Script for transaction logging.

## Overview

This project implements a production-ready C2B callback endpoint that:
- ✅ Validates incoming Daraja C2B payment requests
- ✅ Checks BillRefNumber against a dynamic Google Sheets account list
- ✅ Prevents duplicate transactions
- ✅ Forwards validated transactions to a Google Apps Script webhook for logging
- ✅ Falls back to hardcoded test accounts if Google Sheets is unavailable
- ✅ Responds to Daraja with proper ResultCode within 5 seconds

## Project Structure

```
daraja_one/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── README.md                    # This file
├── daraja_one/                  # Project settings
│   ├── __init__.py
│   ├── settings.py              # Django settings (includes 'api' app)
│   ├── urls.py                  # Main URL router
│   ├── asgi.py
│   └── wsgi.py
└── api/                         # Main API app
    ├── __init__.py
    ├── apps.py
    ├── urls.py                  # API route definitions
    ├── views.py                 # C2B callback view handler
    ├── serializers.py           # DRF serializers for validation
    ├── google_sheets.py         # Google Sheets client with caching
    └── models.py                # (Optional) Transaction model
```

## Installation

### Prerequisites
- Python 3.8+
- pip
- Google Service Account (for Sheets integration, optional)
- Daraja sandbox account (https://developer.safaricom.co.ke/)

### Setup Steps

1. **Clone and navigate to project:**
   ```bash
   cd daraja_one
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

5. **Run migrations (optional, for future DB models):**
   ```bash
   python manage.py migrate
   ```

6. **Start development server:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Google Sheets (optional, falls back to test accounts if not set)
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service-account.json
GOOGLE_SHEET_ID=your-spreadsheet-id-here

# Apps Script Webhook (optional, skips forwarding if not set)
APPS_SCRIPT_URL=https://script.google.com/macros/d/YOUR_SCRIPT_ID/usercallback

# Optional Timeouts
ACCOUNTS_CACHE_TTL=120          # Seconds to cache Sheets data (default: 120)
C2B_HTTP_TIMEOUT=3.0            # HTTP timeout for forwarding (default: 3.0)
```

### Google Service Account Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a service account
3. Generate a JSON key
4. Share your Google Sheet with the service account email
5. Set `GOOGLE_SERVICE_ACCOUNT_FILE` to the path of the JSON key file
6. Set `GOOGLE_SHEET_ID` to your sheet's ID (from the URL)

### Fallback Test Accounts

If Google Sheets is not configured, the endpoint will use these test accounts:
- `600000` (Sandbox ShortCode)
- `600001`, `600002`
- `TEST001`, `TEST002`

## API Endpoints

### C2B Callback Handler
**POST** `/api/daraja/c2b/`

**Request Payload** (Daraja C2B callback format):
```json
{
  "TransactionType": "Pay Bill Online",
  "TransID": "LHG31AA5TX0",
  "TransTime": "20231220120000",
  "TransAmount": 500,
  "BusinessShortCode": "600000",
  "BillRefNumber": "INV-001",
  "InvoiceNumber": "",
  "MSISDN": "254722000000",
  "FirstName": "John",
  "MiddleName": "",
  "LastName": "Doe",
  "OrgAccountBalance": 49500
}
```

**Success Response** (ResultCode 0):
```json
{
  "ResultCode": 0,
  "ResultDesc": "Accepted"
}
```

**Rejection Response** (ResultCode 1):
```json
{
  "ResultCode": 1,
  "ResultDesc": "Rejected: Invalid account"
}
```

### Validation Endpoint (Optional)
**POST** `/api/daraja/validation/`

Responds immediately to Daraja validation checks before C2B.

## Testing

### Quick Test with cURL
```bash
curl -X POST http://localhost:8000/api/daraja/c2b/ \
  -H "Content-Type: application/json" \
  -d '{
    "TransactionType": "Pay Bill Online",
    "TransID": "TEST-001",
    "TransTime": "20260104120000",
    "TransAmount": "100.50",
    "BusinessShortCode": "600000",
    "BillRefNumber": "600000",
    "InvoiceNumber": "",
    "MSISDN": "254700000000",
    "FirstName": "Test",
    "MiddleName": "",
    "LastName": "User",
    "OrgAccountBalance": "50000"
  }'
```

**Expected Response:**
```json
{
  "ResultCode": 0,
  "ResultDesc": "Accepted"
}
```

### Test Duplicate Detection
```bash
# Send same TransID again
curl -X POST http://localhost:8000/api/daraja/c2b/ \
  -H "Content-Type: application/json" \
  -d '{
    ...same payload as above...
  }'

# Should respond:
# {"ResultCode": 1, "ResultDesc": "Rejected: Duplicate transaction"}
```

### Test Invalid Account
```bash
curl -X POST http://localhost:8000/api/daraja/c2b/ \
  -H "Content-Type: application/json" \
  -d '{
    ...
    "BillRefNumber": "INVALID-ACCOUNT",
    ...
  }'

# Should respond:
# {"ResultCode": 1, "ResultDesc": "Rejected: Invalid account"}
```

## Validation Rules

1. **All required fields** must be present: TransactionType, TransID, TransTime, TransAmount, BusinessShortCode, BillRefNumber, MSISDN
2. **TransAmount** must be a positive decimal number
3. **BillRefNumber** must exist in the Google Sheets account list (or fallback list)
4. **TransID** must not have been processed before (duplicate check)
5. **Response time** must be under 5 seconds

## Features

### ✅ Implemented
- POST-only endpoint (rejects GET, PUT, DELETE, etc.)
- JSON validation using DRF serializers
- Duplicate transaction detection (in-memory set)
- Dynamic account validation via Google Sheets API
- Caching to reduce API calls (configurable TTL)
- Fallback to hardcoded test accounts
- Async forwarding to Apps Script with retry logic
- Proper Daraja response codes (0 = accepted, 1 = rejected)
- Comprehensive logging of all validations and errors
- Environment-based configuration

### 🔄 Optional Enhancements
- Persistent duplicate storage in Django ORM
- Transaction history model
- Webhook signature verification
- Rate limiting per account
- Custom error codes
- Request/response audit trail

## Apps Script Integration

Your Google Apps Script should accept POST requests with the full callback payload and log to a sheet:

```javascript
// Google Apps Script function
function doPost(e) {
  const sheet = SpreadsheetApp.getActiveSheet();
  const data = JSON.parse(e.postData.contents);
  
  sheet.appendRow([
    new Date(),
    data.TransID,
    data.BillRefNumber,
    data.MSISDN,
    data.TransAmount,
    data.TransTime,
    'Logged'
  ]);
  
  return ContentService.createTextOutput(JSON.stringify({
    status: 'success'
  })).setMimeType(ContentService.MimeType.JSON);
}
```

## Production Deployment

### Security Checklist
- [ ] Set `DEBUG=False`
- [ ] Update `ALLOWED_HOSTS` with your domain
- [ ] Use strong `SECRET_KEY`
- [ ] Deploy over HTTPS only
- [ ] Keep `GOOGLE_SERVICE_ACCOUNT_FILE` secret (use environment variable)
- [ ] Add rate limiting (e.g., `django-ratelimit`)
- [ ] Enable CORS only for Daraja IPs if needed
- [ ] Use a production database (PostgreSQL recommended)
- [ ] Configure proper logging and error monitoring

### WSGI Deployment
```bash
# Example with Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 daraja_one.wsgi:application
```

### Environment Recommendations
- Use a `.env` file or secrets management service (AWS Secrets Manager, etc.)
- Never commit `.env` to version control
- Use conditional cache headers for Apps Script forwarding
- Monitor transaction logs regularly

## Troubleshooting

### "Invalid JSON payload"
- Ensure Content-Type header is `application/json`
- Check JSON syntax with a validator

### "Rejected: Invalid account"
- Verify BillRefNumber exists in Google Sheet
- Check that service account has read access to the sheet
- Review logs: `GOOGLE_SHEET_ID` may not be set (should use fallback accounts)

### "Rejected: Forwarding failed"
- Verify `APPS_SCRIPT_URL` is correct and reachable
- Check that Apps Script is deployed as web app with public access
- Review Apps Script execution logs

### "Rejected: Server error"
- Check application logs for exceptions
- Verify Google service account file permissions
- Ensure all required environment variables are set

## Logging

The application logs to stdout and file. Set up structured logging in production:

```python
# In settings.py (optional)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'daraja_c2b.log',
        },
    },
    'loggers': {
        'api': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Support & Documentation

- **Daraja Documentation**: https://developer.safaricom.co.ke/docs
- **Django REST Framework**: https://www.django-rest-framework.org/
- **Google Sheets API**: https://developers.google.com/sheets/api

## License

MIT

## Contributing

Pull requests welcome. Please test your changes thoroughly before submitting.
