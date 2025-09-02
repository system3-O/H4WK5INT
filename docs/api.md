# H4WK5INT API Documentation

## Authentication

### Login
```http
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "user",
    "email": "user@example.com",
    "full_name": "User Name",
    "is_admin": false
  }
}
```

### Register
```http
POST /api/auth/register
Content-Type: application/x-www-form-urlencoded

username=new_user&email=user@example.com&password=password&full_name=User Name
```

### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

## Investigations

### Create Investigation
```http
POST /api/investigations/
Authorization: Bearer <token>
Content-Type: application/x-www-form-urlencoded

title=Investigation Title&target=example.com&target_type=domain&description=Description&priority=medium
```

### List Investigations
```http
GET /api/investigations/
Authorization: Bearer <token>
```

### Get Investigation Details
```http
GET /api/investigations/{investigation_id}
Authorization: Bearer <token>
```

### Update Investigation
```http
PUT /api/investigations/{investigation_id}
Authorization: Bearer <token>
Content-Type: application/x-www-form-urlencoded

title=Updated Title&status=completed
```

### Delete Investigation
```http
DELETE /api/investigations/{investigation_id}
Authorization: Bearer <token>
```

## OSINT Modules

### SOCMINT (Social Media Intelligence)
```http
POST /api/osint/socmint
Authorization: Bearer <token>
Content-Type: application/x-www-form-urlencoded

investigation_id=1&query=username&platforms=["twitter","facebook","instagram","linkedin"]
```

### HUMINT (Human Intelligence)
```http
POST /api/osint/humint
Authorization: Bearer <token>
Content-Type: application/x-www-form-urlencoded

investigation_id=1&query=john.doe@example.com&search_types=["email","username","phone","name"]
```

### IMINT (Image Intelligence)
```http
POST /api/osint/imint
Authorization: Bearer <token>
Content-Type: application/x-www-form-urlencoded

investigation_id=1&image_url=https://example.com/image.jpg&analysis_types=["reverse_search","metadata","faces"]
```

### TECHINT (Technical Intelligence)
```http
POST /api/osint/techint
Authorization: Bearer <token>
Content-Type: application/x-www-form-urlencoded

investigation_id=1&target=example.com&scan_types=["dns","subdomains","ports","ssl","whois"]
```

### GEOINT (Geographic Intelligence)
```http
POST /api/osint/geoint
Authorization: Bearer <token>
Content-Type: application/x-www-form-urlencoded

investigation_id=1&query=192.168.1.1&location_types=["ip_geo","address","coordinates"]
```

### WEBINT (Web Intelligence)
```http
POST /api/osint/webint
Authorization: Bearer <token>
Content-Type: application/x-www-form-urlencoded

investigation_id=1&query=search term&search_engines=["google","bing","duckduckgo"]
```

### Available Modules
```http
GET /api/osint/modules
```

## Reports

### Generate Report
```http
POST /api/reports/generate/{investigation_id}
Authorization: Bearer <token>
Content-Type: application/x-www-form-urlencoded

format=pdf
```

**Supported formats:** `pdf`, `markdown`, `json`, `html`

### Download Report
```http
GET /api/reports/download/{filename}
Authorization: Bearer <token>
```

### List Reports
```http
GET /api/reports/list/{investigation_id}
Authorization: Bearer <token>
```

## WebSocket Events

### Real-time Updates
Connect to WebSocket endpoint for real-time investigation updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Investigation update:', data);
};
```

## Error Handling

### Standard Error Response
```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2023-01-01T12:00:00Z"
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

## Rate Limiting

- **Authentication endpoints:** 10 requests per minute
- **OSINT modules:** 100 requests per hour
- **Report generation:** 10 reports per hour

## Examples

### Python Client Example
```python
import requests

# Login
response = requests.post(
    'http://localhost:8000/api/auth/login',
    data={'username': 'user', 'password': 'password'}
)
token = response.json()['access_token']

# Create investigation
headers = {'Authorization': f'Bearer {token}'}
investigation = requests.post(
    'http://localhost:8000/api/investigations/',
    headers=headers,
    data={
        'title': 'Test Investigation',
        'target': 'example.com',
        'target_type': 'domain'
    }
)

# Run TECHINT module
requests.post(
    'http://localhost:8000/api/osint/techint',
    headers=headers,
    data={
        'investigation_id': investigation.json()['id'],
        'target': 'example.com',
        'scan_types': ['dns', 'subdomains', 'whois']
    }
)
```

### JavaScript Client Example
```javascript
// Login
const loginResponse = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'username=user&password=password'
});

const { access_token } = await loginResponse.json();

// Create investigation
const investigation = await fetch('/api/investigations/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: 'title=Test&target=example.com&target_type=domain'
});
```