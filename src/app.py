"""
Boostly - Credit Recognition and Redemption Platform
Main Flask application with all API endpoints
"""
from flask import Flask, request, jsonify
from models import db, Student, Recognition, Endorsement, Redemption
from datetime import datetime
from sqlalchemy import func, desc
import os

app = Flask(__name__)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'boostly.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)


def get_current_month():
    """Get current month in YYYY-MM format"""
    return datetime.utcnow().strftime('%Y-%m')


def reset_monthly_credits(student):
    """
    Automatically reset monthly credits with carry-forward logic (Step-Up Challenge #1)
    
    This function is called automatically on any student access (get_student, create_recognition)
    ensuring credits reset when a new calendar month begins.
    
    Business Rules:
    - Resets available credits to 100 at start of each month
    - Carries forward up to 50 unused credits from previous month
    - Resets monthly sending limit to 0
    - Only resets when calendar month actually changes
    
    Args:
        student: Student object to reset
    """
    current_month = get_current_month()
    
    # Check if reset is needed (only reset when month changes)
    if student.last_reset_month != current_month:
        # Calculate carry-forward credits
        unused_credits = student.available_credits
        carry_forward = min(unused_credits, 50)  # Max 50 credits can be carried forward
        
        # Reset credits
        student.available_credits = 100 + carry_forward
        student.credits_sent_this_month = 0
        student.last_reset_month = current_month
        
        db.session.commit()


@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information"""
    return jsonify({
        'message': 'Welcome to Boostly API',
        'version': '1.0',
        'endpoints': {
            'POST /students': 'Create a new student',
            'GET /students/<id>': 'Get student details',
            'POST /recognition': 'Send recognition with credits',
            'GET /recognitions': 'List all recognitions',
            'POST /endorsement': 'Endorse a recognition',
            'POST /redemption': 'Redeem credits for voucher',
            'GET /redemptions/<student_id>': 'List student redemptions',
            'GET /leaderboard': 'Get top recipients leaderboard',
            'POST /reset-credits/<student_id>': 'Manually trigger credit reset'
        }
    }), 200


# ==================== STUDENT MANAGEMENT ====================

@app.route('/students', methods=['POST'])
def create_student():
    """
    Create a new student
    Request body: { "id": "student_id", "name": "Name", "email": "email@example.com" }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'id' not in data or 'name' not in data or 'email' not in data:
            return jsonify({'error': 'Missing required fields: id, name, email'}), 400
        
        # Check if student already exists
        if Student.query.get(data['id']):
            return jsonify({'error': 'Student with this ID already exists'}), 400
        
        # Check if email already exists
        if Student.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Student with this email already exists'}), 400
        
        # Create new student
        student = Student(
            id=data['id'],
            name=data['name'],
            email=data['email'],
            available_credits=100,
            received_credits=0,
            credits_sent_this_month=0,
            last_reset_month=get_current_month()
        )
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({
            'message': 'Student created successfully',
            'student': student.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    """
    Get student details by ID
    """
    try:
        student = Student.query.get(student_id)
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Auto-reset credits if needed
        reset_monthly_credits(student)
        
        # Get additional stats
        recognitions_sent_count = len(student.recognitions_sent)
        recognitions_received_count = len(student.recognitions_received)
        
        # Calculate total endorsements received
        total_endorsements = db.session.query(func.count(Endorsement.id)).join(
            Recognition, Recognition.id == Endorsement.recognition_id
        ).filter(Recognition.recipient_id == student_id).scalar() or 0
        
        response = student.to_dict()
        response['stats'] = {
            'recognitions_sent': recognitions_sent_count,
            'recognitions_received': recognitions_received_count,
            'total_endorsements_received': total_endorsements
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== RECOGNITION ====================

@app.route('/recognition', methods=['POST'])
def create_recognition():
    """
    Create a recognition (transfer credits from sender to recipient)
    Request body: {
        "sender_id": "student1",
        "recipient_id": "student2",
        "credits": 10,
        "message": "Great work!"
    }
    Business Rules:
    - Cannot send credits to self
    - Credits must be > 0
    - Sender must have sufficient available credits
    - Sender cannot exceed monthly sending limit (100)
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'sender_id' not in data or 'recipient_id' not in data or 'credits' not in data:
            return jsonify({'error': 'Missing required fields: sender_id, recipient_id, credits'}), 400
        
        sender_id = data['sender_id']
        recipient_id = data['recipient_id']
        credits = data['credits']
        message = data.get('message', '')
        
        # Validate credits amount
        if not isinstance(credits, int) or credits <= 0:
            return jsonify({'error': 'Credits must be a positive integer'}), 400
        
        # Rule: Cannot send credits to self
        if sender_id == recipient_id:
            return jsonify({'error': 'Cannot send credits to yourself'}), 400
        
        # Get sender and recipient
        sender = Student.query.get(sender_id)
        recipient = Student.query.get(recipient_id)
        
        if not sender:
            return jsonify({'error': 'Sender not found'}), 404
        if not recipient:
            return jsonify({'error': 'Recipient not found'}), 404
        
        # Auto-reset credits if needed
        reset_monthly_credits(sender)
        reset_monthly_credits(recipient)
        
        # Rule: Check if sender has sufficient available credits
        if sender.available_credits < credits:
            return jsonify({
                'error': 'Insufficient credits',
                'available_credits': sender.available_credits,
                'requested_credits': credits
            }), 400
        
        # Rule: Check monthly sending limit
        if sender.credits_sent_this_month + credits > 100:
            return jsonify({
                'error': 'Monthly sending limit exceeded',
                'monthly_limit': 100,
                'already_sent': sender.credits_sent_this_month,
                'requested_credits': credits,
                'remaining_limit': 100 - sender.credits_sent_this_month
            }), 400
        
        # Process the recognition
        sender.available_credits -= credits
        sender.credits_sent_this_month += credits
        recipient.received_credits += credits
        
        # Create recognition record
        recognition = Recognition(
            sender_id=sender_id,
            recipient_id=recipient_id,
            credits=credits,
            message=message
        )
        
        db.session.add(recognition)
        db.session.commit()
        
        return jsonify({
            'message': 'Recognition created successfully',
            'recognition': recognition.to_dict(),
            'sender_remaining_credits': sender.available_credits,
            'recipient_total_credits': recipient.received_credits
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/recognitions', methods=['GET'])
def list_recognitions():
    """
    List all recognitions
    Query params:
    - student_id: Filter by sender or recipient
    - limit: Limit number of results (default: 50)
    """
    try:
        student_id = request.args.get('student_id')
        limit = request.args.get('limit', 50, type=int)
        
        query = Recognition.query
        
        if student_id:
            query = query.filter(
                (Recognition.sender_id == student_id) | 
                (Recognition.recipient_id == student_id)
            )
        
        recognitions = query.order_by(desc(Recognition.created_at)).limit(limit).all()
        
        return jsonify({
            'count': len(recognitions),
            'recognitions': [r.to_dict() for r in recognitions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ENDORSEMENTS ====================

@app.route('/endorsement', methods=['POST'])
def create_endorsement():
    """
    Endorse a recognition
    Request body: {
        "recognition_id": 1,
        "endorser_id": "student3"
    }
    Business Rules:
    - Each endorser can endorse a recognition only once
    - Endorsements don't affect credit balances
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'recognition_id' not in data or 'endorser_id' not in data:
            return jsonify({'error': 'Missing required fields: recognition_id, endorser_id'}), 400
        
        recognition_id = data['recognition_id']
        endorser_id = data['endorser_id']
        
        # Check if recognition exists
        recognition = Recognition.query.get(recognition_id)
        if not recognition:
            return jsonify({'error': 'Recognition not found'}), 404
        
        # Check if endorser exists
        endorser = Student.query.get(endorser_id)
        if not endorser:
            return jsonify({'error': 'Endorser not found'}), 404
        
        # Rule: Check if already endorsed
        existing_endorsement = Endorsement.query.filter_by(
            recognition_id=recognition_id,
            endorser_id=endorser_id
        ).first()
        
        if existing_endorsement:
            return jsonify({'error': 'You have already endorsed this recognition'}), 400
        
        # Create endorsement
        endorsement = Endorsement(
            recognition_id=recognition_id,
            endorser_id=endorser_id
        )
        
        db.session.add(endorsement)
        db.session.commit()
        
        # Get updated endorsement count
        endorsement_count = Endorsement.query.filter_by(recognition_id=recognition_id).count()
        
        return jsonify({
            'message': 'Endorsement created successfully',
            'endorsement': endorsement.to_dict(),
            'total_endorsements': endorsement_count
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== REDEMPTION ====================

@app.route('/redemption', methods=['POST'])
def create_redemption():
    """
    Redeem credits for voucher
    Request body: {
        "student_id": "student1",
        "credits": 20
    }
    Business Rules:
    - Conversion rate: ₹5 per credit
    - Credits are permanently deducted from received_credits
    - Student can only redeem received credits
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'student_id' not in data or 'credits' not in data:
            return jsonify({'error': 'Missing required fields: student_id, credits'}), 400
        
        student_id = data['student_id']
        credits_to_redeem = data['credits']
        
        # Validate credits amount
        if not isinstance(credits_to_redeem, int) or credits_to_redeem <= 0:
            return jsonify({'error': 'Credits must be a positive integer'}), 400
        
        # Get student
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Auto-reset credits if needed
        reset_monthly_credits(student)
        
        # Rule: Check if student has sufficient received credits
        if student.received_credits < credits_to_redeem:
            return jsonify({
                'error': 'Insufficient received credits to redeem',
                'available_credits': student.received_credits,
                'requested_credits': credits_to_redeem
            }), 400
        
        # Calculate voucher value (₹5 per credit)
        voucher_value = credits_to_redeem * 5
        
        # Deduct credits
        student.received_credits -= credits_to_redeem
        
        # Create redemption record
        redemption = Redemption(
            student_id=student_id,
            credits_redeemed=credits_to_redeem,
            voucher_value=voucher_value
        )
        
        db.session.add(redemption)
        db.session.commit()
        
        return jsonify({
            'message': 'Redemption successful',
            'redemption': redemption.to_dict(),
            'remaining_credits': student.received_credits
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/redemptions/<student_id>', methods=['GET'])
def list_redemptions(student_id):
    """
    List all redemptions for a student
    """
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        redemptions = Redemption.query.filter_by(student_id=student_id).order_by(
            desc(Redemption.created_at)
        ).all()
        
        total_redeemed = sum(r.credits_redeemed for r in redemptions)
        total_value = sum(r.voucher_value for r in redemptions)
        
        return jsonify({
            'student_id': student_id,
            'student_name': student.name,
            'count': len(redemptions),
            'total_credits_redeemed': total_redeemed,
            'total_voucher_value': total_value,
            'redemptions': [r.to_dict() for r in redemptions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== LEADERBOARD (Step-Up Challenge) ====================

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    """
    Get top recipients leaderboard
    Query params:
    - limit: Number of top students to return (default: 10)
    
    Business Rules:
    - Rank by total credits received (descending)
    - If tied, rank by student ID (ascending)
    - Include recognition count and endorsement count
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        # Get all students with their stats
        students = Student.query.all()
        
        leaderboard_data = []
        
        for student in students:
            # Count recognitions received
            recognitions_count = Recognition.query.filter_by(recipient_id=student.id).count()
            
            # Count total endorsements received
            endorsements_count = db.session.query(func.count(Endorsement.id)).join(
                Recognition, Recognition.id == Endorsement.recognition_id
            ).filter(Recognition.recipient_id == student.id).scalar() or 0
            
            leaderboard_data.append({
                'student_id': student.id,
                'student_name': student.name,
                'total_credits_received': student.received_credits,
                'recognitions_received': recognitions_count,
                'total_endorsements': endorsements_count
            })
        
        # Sort by credits (descending), then by student_id (ascending)
        leaderboard_data.sort(key=lambda x: (-x['total_credits_received'], x['student_id']))
        
        # Add rank
        for idx, entry in enumerate(leaderboard_data[:limit], start=1):
            entry['rank'] = idx
        
        return jsonify({
            'leaderboard': leaderboard_data[:limit],
            'total_students': len(students)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== CREDIT RESET (Step-Up Challenge) ====================

@app.route('/reset-credits/<student_id>', methods=['POST'])
def manual_reset_credits(student_id):
    """
    Manually trigger credit reset for a student
    This demonstrates the auto-reset mechanism
    """
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        old_credits = student.available_credits
        old_month = student.last_reset_month
        
        reset_monthly_credits(student)
        
        return jsonify({
            'message': 'Credits reset successfully',
            'student_id': student_id,
            'old_available_credits': old_credits,
            'new_available_credits': student.available_credits,
            'old_reset_month': old_month,
            'new_reset_month': student.last_reset_month,
            'credits_sent_this_month': student.credits_sent_this_month
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== DATABASE INITIALIZATION ====================

@app.route('/init-db', methods=['POST'])
def init_database():
    """Initialize/reset the database"""
    try:
        db.drop_all()
        db.create_all()
        return jsonify({'message': 'Database initialized successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)

