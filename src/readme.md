# Boostly - Credit Recognition & Redemption Platform

> A Flask-based application enabling college students to recognize their peers, allocate monthly credits, and redeem earned rewards.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green)](https://flask.palletsprojects.com/)

---

## 🎯 Overview

Boostly is a comprehensive peer recognition platform that enables students to:
- **Recognize** peers by transferring credits
- **Endorse** recognitions with likes/cheers
- **Redeem** credits for vouchers (₹5 per credit)
- View **leaderboards** of top recipients
- Automatic **monthly credit reset** with carry-forward

### Professional Features 🚀
- **Pydantic Validation**: Type-safe request validation with detailed error messages
- **Rate Limiting**: API abuse protection (customized per endpoint)
- **Secure Error Handling**: No internal error leakage to users
- **Comprehensive Logging**: For debugging and monitoring
- **Automated Credit Reset**: Monthly reset with intelligent carry-forward logic

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Navigate to the src directory**:
```bash
cd src
```

2. **Create a virtual environment** (recommended):
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

### Dependencies
```
Flask==3.0.0              # Web framework
Flask-SQLAlchemy==3.1.1   # ORM
Flask-Limiter==3.5.0      # Rate limiting
pydantic==2.10.5          # Validation
email-validator==2.2.0    # Email validation
python-dateutil==2.8.2    # Date utilities
```

---

## 🚀 Running the Application

### Start the server:
```bash
python app.py
```

The API will be available at: `http://localhost:5000`

### Initialize the database (first time):
```bash
curl -X POST http://localhost:5000/init-db
```

Or the database will be created automatically on first run.

---

## 📚 API Documentation

### Base URL
```
http://localhost:5000
```

### Response Format
All responses are in JSON format.

### Status Codes
| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Successful GET request |
| 201 | Created | Resource successfully created |
| 400 | Bad Request | Validation failed or invalid input |
| 404 | Not Found | Resource doesn't exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error occurred |

---

## 📡 Endpoints

### 1. Create Student

**Endpoint**: `POST /students`  
**Rate Limit**: 10 requests per minute  

**Request Body**:
```json
{
  "id": "2022CS001",
  "name": "Alice Johnson",
  "email": "alice@university.edu"
}
```

**Validation Rules**:
- `id`: Required, 1-50 characters, no whitespace only
- `name`: Required, 1-100 characters, no whitespace only
- `email`: Required, valid email format (validated by email-validator)

**Success Response (201)**:
```json
{
  "message": "Student created successfully",
  "student": {
    "id": "2022CS001",
    "name": "Alice Johnson",
    "email": "alice@university.edu",
    "available_credits": 100,
    "received_credits": 0,
    "credits_sent_this_month": 0,
    "last_reset_month": "2025-11",
    "created_at": "2025-11-13T08:05:30.123456"
  }
}
```

**Error Responses**:
```json
// Validation Error (400)
{
  "error": "Validation failed",
  "details": [
    {
      "loc": ["email"],
      "msg": "value is not a valid email address",
      "type": "value_error"
    }
  ]
}

// Duplicate Student (400)
{
  "error": "Student with this ID already exists"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:5000/students \
  -H "Content-Type: application/json" \
  -d '{
    "id": "2022CS001",
    "name": "Alice Johnson",
    "email": "alice@university.edu"
  }'
```

---

### 2. Get Student Details

**Endpoint**: `GET /students/<student_id>`  
**Rate Limit**: 30 requests per minute  

**Success Response (200)**:
```json
{
  "id": "2022CS001",
  "name": "Alice Johnson",
  "email": "alice@university.edu",
  "available_credits": 100,
  "received_credits": 0,
  "credits_sent_this_month": 0,
  "last_reset_month": "2025-11",
  "created_at": "2025-11-13T08:05:30.123456",
  "stats": {
    "recognitions_sent": 5,
    "recognitions_received": 3,
    "total_endorsements_received": 8
  }
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:5000/students/2022CS001
```

---

### 3. Create Recognition (Transfer Credits)

**Endpoint**: `POST /recognition`  
**Rate Limit**: 20 requests per minute  

**Request Body**:
```json
{
  "sender_id": "2022CS001",
  "recipient_id": "2022CS002",
  "credits": 15,
  "message": "Great job on the project!"
}
```

**Validation Rules**:
- `sender_id`: Required, 1-50 characters
- `recipient_id`: Required, 1-50 characters
- `credits`: Required, 1-100 (positive integer)
- `message`: Optional, max 500 characters

**Business Rules**:
- ✅ Cannot send credits to yourself
- ✅ Must have sufficient available credits
- ✅ Cannot exceed monthly sending limit (100 credits)
- ✅ Credits deducted from sender's available balance
- ✅ Credits added to recipient's received balance

**Success Response (201)**:
```json
{
  "message": "Recognition created successfully",
  "recognition": {
    "id": 1,
    "sender_id": "2022CS001",
    "sender_name": "Alice Johnson",
    "recipient_id": "2022CS002",
    "recipient_name": "Bob Smith",
    "credits": 15,
    "message": "Great job on the project!",
    "endorsement_count": 0,
    "created_at": "2025-11-13T08:10:00.123456"
  },
  "sender_remaining_credits": 85,
  "recipient_total_credits": 15
}
```

**Error Responses**:
```json
// Self-recognition (400)
{
  "error": "Cannot send credits to yourself"
}

// Insufficient credits (400)
{
  "error": "Insufficient credits",
  "available_credits": 10,
  "requested_credits": 15
}

// Monthly limit exceeded (400)
{
  "error": "Monthly sending limit exceeded",
  "monthly_limit": 100,
  "already_sent": 90,
  "requested_credits": 15,
  "remaining_limit": 10
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:5000/recognition \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "2022CS001",
    "recipient_id": "2022CS002",
    "credits": 15,
    "message": "Great job on the project!"
  }'
```

---

### 4. List Recognitions

**Endpoint**: `GET /recognitions`  
**Rate Limit**: 30 requests per minute  

**Query Parameters**:
- `student_id` (optional): Filter by sender or recipient
- `limit` (optional): Limit results (default: 50)

**Success Response (200)**:
```json
{
  "count": 2,
  "recognitions": [
    {
      "id": 2,
      "sender_id": "2022CS003",
      "sender_name": "Charlie Davis",
      "recipient_id": "2022CS001",
      "recipient_name": "Alice Johnson",
      "credits": 20,
      "message": "Excellent teamwork!",
      "endorsement_count": 3,
      "created_at": "2025-11-13T08:15:00.123456"
    },
    {
      "id": 1,
      "sender_id": "2022CS001",
      "sender_name": "Alice Johnson",
      "recipient_id": "2022CS002",
      "recipient_name": "Bob Smith",
      "credits": 15,
      "message": "Great job!",
      "endorsement_count": 0,
      "created_at": "2025-11-13T08:10:00.123456"
    }
  ]
}
```

**cURL Examples**:
```bash
# Get all recognitions
curl -X GET http://localhost:5000/recognitions

# Filter by student
curl -X GET "http://localhost:5000/recognitions?student_id=2022CS001&limit=20"
```

---

### 5. Create Endorsement

**Endpoint**: `POST /endorsement`  
**Rate Limit**: 20 requests per minute  

**Request Body**:
```json
{
  "recognition_id": 1,
  "endorser_id": "2022CS003"
}
```

**Validation Rules**:
- `recognition_id`: Required, positive integer
- `endorser_id`: Required, 1-50 characters

**Business Rules**:
- ✅ Each student can endorse a recognition only once
- ✅ Endorsements don't affect credit balances
- ✅ Just increments endorsement count

**Success Response (201)**:
```json
{
  "message": "Endorsement created successfully",
  "endorsement": {
    "id": 1,
    "recognition_id": 1,
    "endorser_id": "2022CS003",
    "endorser_name": "Charlie Davis",
    "created_at": "2025-11-13T08:12:00.123456"
  },
  "total_endorsements": 1
}
```

**Error Response**:
```json
// Already endorsed (400)
{
  "error": "You have already endorsed this recognition"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:5000/endorsement \
  -H "Content-Type: application/json" \
  -d '{
    "recognition_id": 1,
    "endorser_id": "2022CS003"
  }'
```

---

### 6. Redeem Credits

**Endpoint**: `POST /redemption`  
**Rate Limit**: 10 requests per minute  

**Request Body**:
```json
{
  "student_id": "2022CS002",
  "credits": 10
}
```

**Validation Rules**:
- `student_id`: Required, 1-50 characters
- `credits`: Required, positive integer

**Business Rules**:
- ✅ Conversion rate: **₹5 per credit**
- ✅ Credits permanently deducted from **received_credits**
- ✅ Can only redeem received credits (not available credits)
- ✅ Generates voucher with monetary value

**Success Response (201)**:
```json
{
  "message": "Redemption successful",
  "redemption": {
    "id": 1,
    "student_id": "2022CS002",
    "student_name": "Bob Smith",
    "credits_redeemed": 10,
    "voucher_value": 50.0,
    "created_at": "2025-11-13T08:20:00.123456"
  },
  "remaining_credits": 5
}
```

**Error Response**:
```json
// Insufficient credits (400)
{
  "error": "Insufficient received credits to redeem",
  "available_credits": 5,
  "requested_credits": 10
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:5000/redemption \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "2022CS002",
    "credits": 10
  }'
```

---

### 7. List Redemptions

**Endpoint**: `GET /redemptions/<student_id>`  
**Rate Limit**: 30 requests per minute  

**Success Response (200)**:
```json
{
  "student_id": "2022CS002",
  "student_name": "Bob Smith",
  "count": 2,
  "total_credits_redeemed": 25,
  "total_voucher_value": 125.0,
  "redemptions": [
    {
      "id": 2,
      "student_id": "2022CS002",
      "student_name": "Bob Smith",
      "credits_redeemed": 15,
      "voucher_value": 75.0,
      "created_at": "2025-11-13T08:25:00.123456"
    },
    {
      "id": 1,
      "student_id": "2022CS002",
      "student_name": "Bob Smith",
      "credits_redeemed": 10,
      "voucher_value": 50.0,
      "created_at": "2025-11-13T08:20:00.123456"
    }
  ]
}
```

**cURL Example**:
```bash
curl -X GET http://localhost:5000/redemptions/2022CS002
```

---

### 8. Get Leaderboard (Step-Up Challenge)

**Endpoint**: `GET /leaderboard`  
**Rate Limit**: 30 requests per minute  

**Query Parameters**:
- `limit` (optional): Number of top students (default: 10)

**Business Rules**:
- ✅ Ranked by total credits received (descending)
- ✅ Tie-breaker: student ID (ascending)
- ✅ Includes recognition count and endorsement totals
- ✅ Configurable limit parameter

**Success Response (200)**:
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "student_id": "2022CS002",
      "student_name": "Bob Smith",
      "total_credits_received": 45,
      "recognitions_received": 3,
      "total_endorsements": 5
    },
    {
      "rank": 2,
      "student_id": "2022CS001",
      "student_name": "Alice Johnson",
      "total_credits_received": 30,
      "recognitions_received": 2,
      "total_endorsements": 3
    }
  ],
  "total_students": 5
}
```

**cURL Example**:
```bash
curl -X GET "http://localhost:5000/leaderboard?limit=10"
```

---

### 9. Manual Credit Reset (Step-Up Challenge)

**Endpoint**: `POST /reset-credits/<student_id>`  
**Rate Limit**: Default limits  

**Success Response (200)**:
```json
{
  "message": "Credits reset successfully",
  "student_id": "2022CS001",
  "old_available_credits": 35,
  "new_available_credits": 135,
  "old_reset_month": "2025-10",
  "new_reset_month": "2025-11",
  "credits_sent_this_month": 0
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:5000/reset-credits/2022CS001
```

**Note**: This endpoint is for testing. In production, credit reset happens **automatically** when:
- `GET /students/<id>` is called
- `POST /recognition` is called
- Any other endpoint that accesses student data

---

## 📜 Business Rules

### Recognition Rules
- ✅ Each student receives **100 credits every month**
- ✅ **Cannot send credits to yourself** (self-recognition not allowed)
- ✅ **Monthly sending limit**: 100 credits per calendar month
- ✅ Cannot send more credits than available balance
- ✅ Cannot exceed monthly sending limit
- ✅ Credits deducted from sender's `available_credits`
- ✅ Credits added to recipient's `received_credits`

### Endorsement Rules
- ✅ Each endorser can endorse a recognition **only once**
- ✅ Enforced by unique constraint: (recognition_id, endorser_id)
- ✅ Endorsements are just a count
- ✅ **No effect on credit balances**
- ✅ Can endorse any recognition (including your own)

### Redemption Rules
- ✅ Conversion rate: **₹5 per credit**
- ✅ Credits are **permanently deducted** from `received_credits`
- ✅ Can only redeem **received credits** (not available credits)
- ✅ Generates voucher with monetary value
- ✅ No limit on redemption amount (as long as sufficient received credits)

### Credit Reset Rules (Step-Up Challenge - Automated)
- ✅ Available credits reset to **100 at start of each month**
- ✅ Up to **50 unused credits** can be carried forward
- ✅ If > 50 unused credits, only 50 carry forward
- ✅ Monthly sending limit (`credits_sent_this_month`) resets to **0**
- ✅ **Automatic**: Triggers on any API call that accesses student data
- ✅ Only resets when calendar month actually changes
- ✅ Tracked via `last_reset_month` field (YYYY-MM format)

### Leaderboard Rules (Step-Up Challenge)
- ✅ Ranked by **total credits received** (descending)
- ✅ Tie-breaker: **student ID** (ascending - alphabetical)
- ✅ Includes **recognition count** (recognitions received)
- ✅ Includes **total endorsements** (endorsements on received recognitions)
- ✅ Configurable **limit parameter**
- ✅ Returns rank, student info, stats

---

## 🏗️ Architecture

### Technology Stack
- **Framework**: Flask 3.0.0
- **ORM**: SQLAlchemy (Flask-SQLAlchemy 3.1.1)
- **Database**: SQLite
- **Validation**: Pydantic 2.10.5
- **Rate Limiting**: Flask-Limiter 3.5.0
- **Email Validation**: email-validator 2.2.0
- **Logging**: Python logging module

### Project Structure
```
src/
├── app.py                  # Main Flask application
├── models.py               # SQLAlchemy database models
├── schemas.py              # Pydantic validation schemas
├── requirements.txt        # Python dependencies
├── readme.md              # This file
├── test_api.ps1           # Automated test suite
├── test_month_change.py   # Credit reset tests
├── test_specific_rules.ps1 # Business rule tests
└── boostly.db             # SQLite database (created on first run)
```

### Database Schema

**Students Table** (`students`):
```sql
id                      VARCHAR(50) PRIMARY KEY
name                    VARCHAR(100) NOT NULL
email                   VARCHAR(100) UNIQUE NOT NULL
available_credits       INTEGER DEFAULT 100 NOT NULL
received_credits        INTEGER DEFAULT 0 NOT NULL
credits_sent_this_month INTEGER DEFAULT 0 NOT NULL
last_reset_month        VARCHAR(7)  -- Format: YYYY-MM
created_at              DATETIME
```

**Recognitions Table** (`recognitions`):
```sql
id            INTEGER PRIMARY KEY AUTOINCREMENT
sender_id     VARCHAR(50) FOREIGN KEY -> students.id
recipient_id  VARCHAR(50) FOREIGN KEY -> students.id
credits       INTEGER NOT NULL
message       TEXT
created_at    DATETIME
```

**Endorsements Table** (`endorsements`):
```sql
id              INTEGER PRIMARY KEY AUTOINCREMENT
recognition_id  INTEGER FOREIGN KEY -> recognitions.id
endorser_id     VARCHAR(50) FOREIGN KEY -> students.id
created_at      DATETIME
UNIQUE (recognition_id, endorser_id)  -- Prevents duplicate endorsements
```

**Redemptions Table** (`redemptions`):
```sql
id               INTEGER PRIMARY KEY AUTOINCREMENT
student_id       VARCHAR(50) FOREIGN KEY -> students.id
credits_redeemed INTEGER NOT NULL
voucher_value    FLOAT NOT NULL  -- In ₹
created_at       DATETIME
```

---

## 🛡️ Security & Validation

### 1. Pydantic Validation
All POST endpoints use Pydantic models for request validation:

**StudentCreate Schema**:
- `id`: 1-50 chars, no whitespace only
- `name`: 1-100 chars, no whitespace only
- `email`: Valid email format (EmailStr with email-validator)

**RecognitionCreate Schema**:
- `sender_id`: 1-50 chars
- `recipient_id`: 1-50 chars
- `credits`: 1-100 (positive integer)
- `message`: Optional, max 500 chars

**EndorsementCreate Schema**:
- `recognition_id`: Positive integer
- `endorser_id`: 1-50 chars

**RedemptionCreate Schema**:
- `student_id`: 1-50 chars
- `credits`: Positive integer

**Validation Error Example**:
```json
{
  "error": "Validation failed",
  "details": [
    {
      "loc": ["email"],
      "msg": "value is not a valid email address: An email address must have an @-sign.",
      "type": "value_error"
    }
  ]
}
```

### 2. Rate Limiting
Protection against API abuse with customized limits per endpoint:

| Endpoint Type | Limit | Reason |
|---------------|-------|--------|
| Create Student | 10/min | Prevent spam registration |
| Get Student | 30/min | Allow frequent reads |
| Recognition | 20/min | Balance usage vs protection |
| List Recognitions | 30/min | Allow frequent browsing |
| Endorsement | 20/min | Prevent endorsement spam |
| Redemption | 10/min | Sensitive financial operation |
| List Redemptions | 30/min | Allow frequent checks |
| Leaderboard | 30/min | Allow frequent viewing |
| Global Default | 200/day, 50/hour | Overall protection |

**Rate Limit Error (429)**:
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please slow down and try again later."
}
```

### 3. Error Handling
**Secure Error Messages**:
- ✅ No internal error details leaked to users
- ✅ Generic error messages for server errors
- ✅ Detailed logging for debugging (server-side only)
- ✅ Specific error messages for validation and business rules

**Error Handlers**:
- `400`: Bad Request (validation failed)
- `404`: Not Found (resource doesn't exist)
- `405`: Method Not Allowed
- `429`: Rate Limit Exceeded
- `500`: Internal Server Error (generic message)

### 4. Database Security
- ✅ **SQLAlchemy ORM**: Prevents SQL injection
- ✅ **Unique Constraints**: Database-level duplicate prevention
- ✅ **Foreign Key Constraints**: Maintains referential integrity
- ✅ **Transaction Management**: Automatic rollback on errors

### 5. Logging
**Comprehensive logging throughout the application**:
- INFO: Successful operations (student created, recognition made, etc.)
- ERROR: Database errors, unexpected exceptions
- WARNING: Rate limit exceeded
- All logs include relevant context (student IDs, amounts, etc.)

---

## 🧪 Testing

### Automated Test Suite

**Run all tests**:
```powershell
.\test_api.ps1
```

**Test Coverage**:
- ✅ Student creation and retrieval
- ✅ Recognition with business rule validation
- ✅ Self-recognition prevention
- ✅ Endorsement with duplicate prevention
- ✅ Redemption system
- ✅ Leaderboard generation
- ✅ Credit reset mechanism
- ✅ Monthly sending limit enforcement

**Run credit reset tests**:
```bash
python test_month_change.py
```

**Run business rule tests**:
```powershell
.\test_specific_rules.ps1
```

### Manual Testing

See `../test-cases/test-cases.txt` for detailed test scenarios, expected results, and step-by-step instructions.

### Sample Test Workflow

1. **Initialize Database**:
```bash
curl -X POST http://localhost:5000/init-db
```

2. **Create Students**:
```bash
curl -X POST http://localhost:5000/students -H "Content-Type: application/json" \
  -d '{"id":"2022CS001","name":"Alice","email":"alice@university.edu"}'

curl -X POST http://localhost:5000/students -H "Content-Type: application/json" \
  -d '{"id":"2022CS002","name":"Bob","email":"bob@university.edu"}'
```

3. **Send Recognition**:
```bash
curl -X POST http://localhost:5000/recognition -H "Content-Type: application/json" \
  -d '{"sender_id":"2022CS001","recipient_id":"2022CS002","credits":15,"message":"Great work!"}'
```

4. **Endorse Recognition**:
```bash
curl -X POST http://localhost:5000/endorsement -H "Content-Type: application/json" \
  -d '{"recognition_id":1,"endorser_id":"2022CS001"}'
```

5. **Redeem Credits**:
```bash
curl -X POST http://localhost:5000/redemption -H "Content-Type: application/json" \
  -d '{"student_id":"2022CS002","credits":10}'
```

6. **View Leaderboard**:
```bash
curl -X GET "http://localhost:5000/leaderboard?limit=10"
```

---

## 🔧 Configuration

### Rate Limit Configuration
Edit `app.py` to customize rate limits:

```python
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],  # Adjust global limits
    storage_uri="memory://"
)

# Adjust per-endpoint limits
@app.route('/students', methods=['POST'])
@limiter.limit("10 per minute")  # Customize this
def create_student():
    ...
```

### Database Configuration
By default, SQLite database is stored at `src/boostly.db`.

To change database location, edit `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///path/to/your/database.db'
```

### Logging Configuration
Adjust logging level in `app.py`:
```python
logging.basicConfig(level=logging.INFO)  # Change to DEBUG for more details
```

---

## 📊 Performance Considerations

### Credit Reset Optimization
- Reset only triggers when month changes (checked via `last_reset_month`)
- Minimal database queries (single update)
- Automatic triggering prevents manual intervention

### Database Indexing
- Primary keys on all tables
- Foreign key indexes for relationships
- Unique constraint on (recognition_id, endorser_id) for fast duplicate checks

### Rate Limiting
- Memory-based storage for fast access
- Per-IP tracking prevents single-source abuse
- Customized limits per endpoint type

---

## 🚨 Troubleshooting

### Issue: "Rate limit exceeded"
**Solution**: Wait for the rate limit window to expire, or adjust limits in code.

### Issue: "Database error occurred"
**Solution**: 
- Check if `boostly.db` file has write permissions
- Try deleting `boostly.db` and reinitializing with `/init-db`

### Issue: "Validation failed"
**Solution**: Check the `details` array in the error response for specific field errors.

### Issue: Credits not resetting
**Solution**: 
- Reset is automatic but only when month changes
- Use `/reset-credits/<student_id>` to manually trigger for testing
- Check `last_reset_month` field in student record

---

## 📄 License

This project is created as part of the Rippling AI Coding Round.

---

## 👤 Author

**Harsh Anand**  
Student ID: 2K22/CO/195  

---

## 🙏 Acknowledgments

- Built with Flask and Python
- Uses Pydantic for robust validation
- Implements Flask-Limiter for API protection
- SQLAlchemy for elegant database management
- email-validator for email validation

---

**⭐ For questions or issues, please refer to the test cases documentation or review the inline code comments.**
