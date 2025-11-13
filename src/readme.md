# Boostly - Credit Recognition and Redemption Platform

A Flask-based application that enables college students to recognize their peers, allocate monthly credits, and redeem earned rewards.

## Table of Contents
- [Features](#features)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Sample Requests and Responses](#sample-requests-and-responses)
- [Business Rules](#business-rules)

## Features

### Core Functionality
1. **Recognition System**: Transfer credits between students with monthly limits
2. **Endorsements**: Like/cheer recognition entries
3. **Redemption**: Convert received credits to vouchers (₹5 per credit)

### Step-Up Challenges
1. **Credit Reset**: Automatic monthly reset with carry-forward (up to 50 credits)
2. **Leaderboard**: Top recipients by credits received with endorsement counts

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Navigate to the src directory**
```bash
cd src
```

2. **Create a virtual environment (recommended)**
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize the database**
The database will be automatically created when you first run the application, or you can use the `/init-db` endpoint.

## Running the Application

### Start the Flask server
```bash
python app.py
```

The application will start on `http://localhost:5000`

### Initialize Database (First Time)
```bash
curl -X POST http://localhost:5000/init-db
```

## API Documentation

### Base URL
```
http://localhost:5000
```

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and available endpoints |
| POST | `/students` | Create a new student |
| GET | `/students/<id>` | Get student details and stats |
| POST | `/recognition` | Send recognition with credits |
| GET | `/recognitions` | List all recognitions |
| POST | `/endorsement` | Endorse a recognition |
| POST | `/redemption` | Redeem credits for voucher |
| GET | `/redemptions/<student_id>` | List student's redemptions |
| GET | `/leaderboard` | Get top recipients leaderboard |
| POST | `/reset-credits/<student_id>` | Manually trigger credit reset |
| POST | `/init-db` | Initialize/reset database |

---

## Sample Requests and Responses

### 1. Create Student

**Request:**
```bash
curl -X POST http://localhost:5000/students \
  -H "Content-Type: application/json" \
  -d '{
    "id": "2022CS001",
    "name": "Alice Johnson",
    "email": "alice@university.edu"
  }'
```

**Response:**
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

---

### 2. Get Student Details

**Request:**
```bash
curl -X GET http://localhost:5000/students/2022CS001
```

**Response:**
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
    "recognitions_sent": 0,
    "recognitions_received": 0,
    "total_endorsements_received": 0
  }
}
```

---

### 3. Create Recognition (Transfer Credits)

**Request:**
```bash
curl -X POST http://localhost:5000/recognition \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "2022CS001",
    "recipient_id": "2022CS002",
    "credits": 15,
    "message": "Great job on the project presentation!"
  }'
```

**Response:**
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
    "message": "Great job on the project presentation!",
    "endorsement_count": 0,
    "created_at": "2025-11-13T08:10:00.123456"
  },
  "sender_remaining_credits": 85,
  "recipient_total_credits": 15
}
```

**Error Example (Self-recognition):**
```json
{
  "error": "Cannot send credits to yourself"
}
```

**Error Example (Insufficient credits):**
```json
{
  "error": "Insufficient credits",
  "available_credits": 10,
  "requested_credits": 15
}
```

**Error Example (Monthly limit exceeded):**
```json
{
  "error": "Monthly sending limit exceeded",
  "monthly_limit": 100,
  "already_sent": 90,
  "requested_credits": 15,
  "remaining_limit": 10
}
```

---

### 4. List Recognitions

**Request (All):**
```bash
curl -X GET http://localhost:5000/recognitions
```

**Request (Filtered by student):**
```bash
curl -X GET "http://localhost:5000/recognitions?student_id=2022CS001&limit=20"
```

**Response:**
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
      "message": "Great job on the project presentation!",
      "endorsement_count": 0,
      "created_at": "2025-11-13T08:10:00.123456"
    }
  ]
}
```

---

### 5. Create Endorsement

**Request:**
```bash
curl -X POST http://localhost:5000/endorsement \
  -H "Content-Type: application/json" \
  -d '{
    "recognition_id": 1,
    "endorser_id": "2022CS003"
  }'
```

**Response:**
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

**Error Example (Already endorsed):**
```json
{
  "error": "You have already endorsed this recognition"
}
```

---

### 6. Redeem Credits

**Request:**
```bash
curl -X POST http://localhost:5000/redemption \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "2022CS002",
    "credits": 10
  }'
```

**Response:**
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

**Error Example (Insufficient credits):**
```json
{
  "error": "Insufficient received credits to redeem",
  "available_credits": 5,
  "requested_credits": 10
}
```

---

### 7. List Redemptions

**Request:**
```bash
curl -X GET http://localhost:5000/redemptions/2022CS002
```

**Response:**
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

---

### 8. Get Leaderboard

**Request:**
```bash
curl -X GET "http://localhost:5000/leaderboard?limit=5"
```

**Response:**
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
    },
    {
      "rank": 3,
      "student_id": "2022CS003",
      "student_name": "Charlie Davis",
      "total_credits_received": 20,
      "recognitions_received": 1,
      "total_endorsements": 1
    }
  ],
  "total_students": 5
}
```

---

### 9. Manual Credit Reset

**Request:**
```bash
curl -X POST http://localhost:5000/reset-credits/2022CS001
```

**Response:**
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

---

## Business Rules

### Recognition Rules
1. Each student receives **100 credits every month** (reset at start of calendar month)
2. **Cannot send credits to yourself** (self-recognition not allowed)
3. **Monthly sending limit**: 100 credits per calendar month
4. Cannot send more credits than current balance
5. Cannot exceed monthly sending limit

### Endorsement Rules
1. Each endorser can endorse a recognition **only once**
2. Endorsements are just a count - they **don't affect credit balances**

### Redemption Rules
1. Credits converted to vouchers at **₹5 per credit**
2. Credits are **permanently deducted** from received balance
3. Can only redeem **received credits** (not available/sending credits)

### Credit Reset Rules (Step-Up Challenge)
1. Available credits reset to **100 at start of each month**
2. Up to **50 unused credits** can be carried forward
3. If more than 50 unused credits, only 50 carry forward
4. Monthly sending limit resets to 100
5. Auto-reset happens on any API call that accesses student data

### Leaderboard Rules (Step-Up Challenge)
1. Rank by **total credits received** (descending)
2. Tie-breaker: **student ID** (ascending)
3. Includes **recognition count** and **endorsement totals**
4. Support for **limit parameter**

---

## Database Schema

### Students Table
- `id` (String, Primary Key): Student ID
- `name` (String): Student name
- `email` (String, Unique): Student email
- `available_credits` (Integer): Credits available to send
- `received_credits` (Integer): Credits received from others
- `credits_sent_this_month` (Integer): Track monthly sending
- `last_reset_month` (String): Last reset month (YYYY-MM)
- `created_at` (DateTime): Creation timestamp

### Recognitions Table
- `id` (Integer, Primary Key): Recognition ID
- `sender_id` (Foreign Key): Sender student ID
- `recipient_id` (Foreign Key): Recipient student ID
- `credits` (Integer): Credits transferred
- `message` (Text): Recognition message
- `created_at` (DateTime): Creation timestamp

### Endorsements Table
- `id` (Integer, Primary Key): Endorsement ID
- `recognition_id` (Foreign Key): Recognition being endorsed
- `endorser_id` (Foreign Key): Endorser student ID
- `created_at` (DateTime): Creation timestamp
- Unique constraint on (recognition_id, endorser_id)

### Redemptions Table
- `id` (Integer, Primary Key): Redemption ID
- `student_id` (Foreign Key): Student redeeming credits
- `credits_redeemed` (Integer): Credits redeemed
- `voucher_value` (Float): Voucher value in ₹
- `created_at` (DateTime): Creation timestamp

---

## Technology Stack
- **Framework**: Flask 3.0.0
- **Database**: SQLite (via Flask-SQLAlchemy)
- **ORM**: SQLAlchemy
- **Date Handling**: python-dateutil

---

## Testing

See `../test-cases/test-cases.txt` for detailed test case documentation.

---

## Author
Built with Flask and Python for the Rippling AI Coding Round

