"""
Database models for Boostly application
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

db = SQLAlchemy()


class Student(db.Model):
    """Student model for storing student information and credit tracking"""
    __tablename__ = 'students'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    available_credits = db.Column(db.Integer, default=100, nullable=False)  # Credits available to send
    received_credits = db.Column(db.Integer, default=0, nullable=False)  # Credits received from others
    credits_sent_this_month = db.Column(db.Integer, default=0, nullable=False)  # Track monthly sending
    last_reset_month = db.Column(db.String(7), nullable=True)  # Format: YYYY-MM
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    recognitions_sent = db.relationship('Recognition', foreign_keys='Recognition.sender_id', backref='sender', lazy=True)
    recognitions_received = db.relationship('Recognition', foreign_keys='Recognition.recipient_id', backref='recipient', lazy=True)
    redemptions = db.relationship('Redemption', backref='student', lazy=True)
    
    def to_dict(self):
        """Convert student object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'available_credits': self.available_credits,
            'received_credits': self.received_credits,
            'credits_sent_this_month': self.credits_sent_this_month,
            'last_reset_month': self.last_reset_month,
            'created_at': self.created_at.isoformat()
        }


class Recognition(db.Model):
    """Recognition model for storing credit transfers between students"""
    __tablename__ = 'recognitions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.String(50), db.ForeignKey('students.id'), nullable=False)
    recipient_id = db.Column(db.String(50), db.ForeignKey('students.id'), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    endorsements = db.relationship('Endorsement', backref='recognition', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert recognition object to dictionary"""
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.name,
            'recipient_id': self.recipient_id,
            'recipient_name': self.recipient.name,
            'credits': self.credits,
            'message': self.message,
            'endorsement_count': len(self.endorsements),
            'created_at': self.created_at.isoformat()
        }


class Endorsement(db.Model):
    """Endorsement model for storing likes/cheers on recognitions"""
    __tablename__ = 'endorsements'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recognition_id = db.Column(db.Integer, db.ForeignKey('recognitions.id'), nullable=False)
    endorser_id = db.Column(db.String(50), db.ForeignKey('students.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to ensure one endorsement per student per recognition
    __table_args__ = (
        db.UniqueConstraint('recognition_id', 'endorser_id', name='unique_endorsement'),
    )
    
    # Relationship
    endorser = db.relationship('Student', backref='endorsements', lazy=True)
    
    def to_dict(self):
        """Convert endorsement object to dictionary"""
        return {
            'id': self.id,
            'recognition_id': self.recognition_id,
            'endorser_id': self.endorser_id,
            'endorser_name': self.endorser.name,
            'created_at': self.created_at.isoformat()
        }


class Redemption(db.Model):
    """Redemption model for tracking credit redemptions"""
    __tablename__ = 'redemptions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.String(50), db.ForeignKey('students.id'), nullable=False)
    credits_redeemed = db.Column(db.Integer, nullable=False)
    voucher_value = db.Column(db.Float, nullable=False)  # In ₹
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert redemption object to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.name,
            'credits_redeemed': self.credits_redeemed,
            'voucher_value': self.voucher_value,
            'created_at': self.created_at.isoformat()
        }

