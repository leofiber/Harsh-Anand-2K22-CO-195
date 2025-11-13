# Boostly - Credit Recognition & Redemption Platform

> A Flask-based application enabling college students to recognize their peers, allocate monthly credits, and redeem earned rewards.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Features

### Core Functionality
- **Recognition System**: Transfer credits between students with comprehensive business rule validation
- **Endorsements**: Like/cheer recognition entries with duplicate prevention
- **Redemption**: Convert received credits to vouchers (₹5 per credit)

### Step-Up Challenges ⭐
- **Automatic Credit Reset**: Monthly reset with up to 50 unused credits carry-forward
- **Leaderboard**: Top recipients ranked by credits with endorsement statistics

### Professional Features 🚀
- **Pydantic Validation**: Type-safe request validation with detailed error messages
- **Rate Limiting**: Protects against API abuse (configurable per endpoint)
- **Secure Error Handling**: No internal error leakage to end users
- **Logging**: Comprehensive logging for debugging and monitoring

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [API Documentation](#api-documentation)
- [Business Rules](#business-rules)
- [Architecture](#architecture)
- [Testing](#testing)
- [Rate Limits](#rate-limits)

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/leofiber/Harsh-Anand-2K22-CO-195.git
cd Harsh-Anand-2K22-CO-195

# Install dependencies
cd src
pip install -r requirements.txt

# Run the application
python app.py
```

The API will be available at `http://localhost:5000`

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Dependencies
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Limiter==3.5.0
pydantic==2.5.0
python-dateutil==2.8.2
```

### Setup Steps

1. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Initialize the database** (automatic on first run):
```bash
python app.py
```

Or manually:
```bash
curl -X POST http://localhost:5000/init-db
```

---

## 📚 API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints Overview

| Method | Endpoint | Rate Limit | Description |
|--------|----------|------------|-------------|
| GET | `/` | 200/day | API information |
| POST | `/students` | 10/min | Create a student |
| GET | `/students/<id>` | 30/min | Get student details |
| POST | `/recognition` | 20/min | Create recognition |
| GET | `/recognitions` | 30/min | List recognitions |
| POST | `/endorsement` | 20/min | Endorse recognition |
| POST | `/redemption` | 10/min | Redeem credits |
| GET | `/redemptions/<id>` | 30/min | List redemptions |
| GET | `/leaderboard` | 30/min | Get leaderboard |

---

### 1. Create Student

**Endpoint**: `POST /students`

**Request Body**:
```json
{
  "id": "2022CS001",
  "name": "Alice Johnson",
  "email": "alice@university.edu"
}
```

**Validation**:
- `id`: Required, 1-50 characters
- `name`: Required, 1-100 characters, no whitespace only
- `email`: Required, valid email format

**Response (201)**:
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
- `400`: Validation failed / Student already exists
- `429`: Rate limit exceeded
- `500`: Server error

---

### 2. Create Recognition

**Endpoint**: `POST /recognition`

**Request Body**:
```json
{
  "sender_id": "2022CS001",
  "recipient_id": "2022CS002",
  "credits": 15,
  "message": "Great job on the project!"
}
```

**Validation**:
- `sender_id`: Required, 1-50 characters
- `recipient_id`: Required, 1-50 characters
- `credits`: Required, 1-100 (positive integer)
- `message`: Optional, max 500 characters

**Response (201)**:
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

**Business Rule Errors**:
- Cannot send credits to self
- Insufficient available credits
- Monthly sending limit exceeded (100 credits/month)

---

### 3. Create Endorsement

**Endpoint**: `POST /endorsement`

**Request Body**:
```json
{
  "recognition_id": 1,
  "endorser_id": "2022CS003"
}
```

**Validation**:
- `recognition_id`: Required, positive integer
- `endorser_id`: Required, 1-50 characters

**Response (201)**:
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

---

### 4. Redeem Credits

**Endpoint**: `POST /redemption`

**Request Body**:
```json
{
  "student_id": "2022CS002",
  "credits": 10
}
```

**Validation**:
- `student_id`: Required, 1-50 characters
- `credits`: Required, positive integer

**Response (201)**:
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

---

### 5. Get Leaderboard

**Endpoint**: `GET /leaderboard?limit=10`

**Query Parameters**:
- `limit`: Optional, default 10

**Response (200)**:
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
    }
  ],
  "total_students": 5
}
```

---

## 📜 Business Rules

### Recognition Rules
- ✅ Each student receives **100 credits every month**
- ✅ **Cannot send credits to yourself**
- ✅ **Monthly sending limit**: 100 credits per calendar month
- ✅ Cannot send more credits than available balance
- ✅ Credits are deducted from sender's available balance
- ✅ Credits are added to recipient's received balance

### Endorsement Rules
- ✅ Each student can endorse a recognition **only once**
- ✅ Endorsements are just a count
- ✅ **No effect on credit balances**

### Redemption Rules
- ✅ Conversion rate: **₹5 per credit**
- ✅ Credits are **permanently deducted** from received balance
- ✅ Can only redeem **received credits** (not available credits)
- ✅ Generates voucher with monetary value

### Credit Reset Rules (Automated)
- ✅ Available credits reset to **100 at start of each month**
- ✅ Up to **50 unused credits** can be carried forward
- ✅ Monthly sending limit resets to 0
- ✅ **Automatic**: Triggers on any API call that accesses student data

### Leaderboard Rules
- ✅ Ranked by **total credits received** (descending)
- ✅ Tie-breaker: **student ID** (ascending)
- ✅ Includes **recognition count** and **endorsement totals**
- ✅ Configurable limit parameter

---

## 🏗️ Architecture

### Technology Stack
- **Framework**: Flask 3.0.0
- **ORM**: SQLAlchemy (Flask-SQLAlchemy 3.1.1)
- **Database**: SQLite
- **Validation**: Pydantic 2.5.0
- **Rate Limiting**: Flask-Limiter 3.5.0
- **Logging**: Python logging module

### Project Structure
```
Harsh-Anand-2K22-CO-195/
├── src/
│   ├── app.py                  # Main Flask application
│   ├── models.py               # SQLAlchemy database models
│   ├── schemas.py              # Pydantic validation schemas
│   ├── requirements.txt        # Python dependencies
│   ├── readme.md              # API documentation
│   └── test_api.ps1           # Automated test suite
├── prompt/
│   └── llm-chat-export.txt    # AI assistant conversation
├── test-cases/
│   └── test-cases.txt         # Test documentation
├── .gitignore
└── README.md                   # This file
```

### Database Schema

**Students Table**:
- `id` (PK): Student ID
- `name`: Student name
- `email` (Unique): Email address
- `available_credits`: Credits available to send
- `received_credits`: Credits received from others
- `credits_sent_this_month`: Monthly sending tracker
- `last_reset_month`: Last reset month (YYYY-MM)
- `created_at`: Creation timestamp

**Recognitions Table**:
- `id` (PK): Recognition ID
- `sender_id` (FK): Sender student ID
- `recipient_id` (FK): Recipient student ID
- `credits`: Credits transferred
- `message`: Recognition message
- `created_at`: Creation timestamp

**Endorsements Table**:
- `id` (PK): Endorsement ID
- `recognition_id` (FK): Recognition being endorsed
- `endorser_id` (FK): Endorser student ID
- `created_at`: Creation timestamp
- **Unique Constraint**: (recognition_id, endorser_id)

**Redemptions Table**:
- `id` (PK): Redemption ID
- `student_id` (FK): Student redeeming
- `credits_redeemed`: Credits redeemed
- `voucher_value`: Voucher value in ₹
- `created_at`: Creation timestamp

---

## 🧪 Testing

### Run Automated Tests
```powershell
cd src
.\test_api.ps1
```

### Test Coverage
- ✅ Student creation and retrieval
- ✅ Recognition with business rule validation
- ✅ Self-recognition prevention
- ✅ Endorsement with duplicate prevention
- ✅ Redemption system
- ✅ Leaderboard generation
- ✅ Credit reset mechanism
- ✅ Monthly sending limit enforcement

### Manual Testing
See `test-cases/test-cases.txt` for detailed test scenarios and expected results.

---

## 🛡️ Rate Limits

| Endpoint Type | Limit | Reason |
|---------------|-------|--------|
| Create Student | 10/min | Prevent spam registration |
| Recognition | 20/min | Balance usage vs protection |
| Endorsement | 20/min | Prevent endorsement spam |
| Redemption | 10/min | Sensitive financial operation |
| Read Operations | 30/min | Allow frequent reads |
| Global Default | 200/day, 50/hour | Overall protection |

**Rate Limit Response (429)**:
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please slow down and try again later."
}
```

---

## 🔒 Security Features

### 1. Input Validation
- **Pydantic Models**: Type-safe validation with detailed error messages
- **Field Constraints**: Length limits, format validation, range checks
- **Sanitization**: Whitespace stripping, empty string handling

### 2. Error Handling
- **No Internal Error Leakage**: Generic error messages to end users
- **Detailed Logging**: Internal logs for debugging
- **Graceful Degradation**: Proper error responses with appropriate HTTP codes

### 3. Rate Limiting
- **Per-Endpoint Limits**: Customized for each operation type
- **IP-Based Tracking**: Prevents single source abuse
- **Automatic Blocking**: Temporary blocks on limit exceed

### 4. Database Protection
- **SQLAlchemy ORM**: Prevents SQL injection
- **Unique Constraints**: Database-level duplicate prevention
- **Foreign Key Constraints**: Maintains referential integrity

---

## 📝 API Response Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET request |
| 201 | Created | Successful POST (resource created) |
| 400 | Bad Request | Validation failed / Invalid input |
| 404 | Not Found | Resource doesn't exist |
| 405 | Method Not Allowed | Wrong HTTP method |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |

---

## 👥 Author

**Harsh Anand**  
Student ID: 2K22/CO/195  
Repository: [github.com/leofiber/Harsh-Anand-2K22-CO-195](https://github.com/leofiber/Harsh-Anand-2K22-CO-195)

---

## 📄 License

This project is created as part of the Rippling AI Coding Round.

---

## 🙏 Acknowledgments

- Built with Flask and Python
- Uses Pydantic for robust validation
- Implements Flask-Limiter for API protection
- SQLAlchemy for database management

---

## 📧 Support

For issues or questions, please create an issue on the GitHub repository.

---

**⭐ Star this repo if you find it useful!**
