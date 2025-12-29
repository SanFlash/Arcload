"""
Database models for Arcaload
Admin, Game, and GameRequest models
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Admin(db.Model):
    """Admin user model"""
    __tablename__ = 'admin'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    games = db.relationship('Game', backref='admin', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Admin {self.username}>'


class Game(db.Model):
    """Game model"""
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    cover_image_url = db.Column(db.String(500), nullable=False)
    download_link = db.Column(db.String(500), nullable=False)
    downloads = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)
    
    def __repr__(self):
        return f'<Game {self.title}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'genre': self.genre,
            'cover_image_url': self.cover_image_url,
            'download_link': self.download_link,
            'downloads': self.downloads,
            'created_at': self.created_at.isoformat()
        }


class GameRequest(db.Model):
    """Game request model for user-requested games"""
    __tablename__ = 'game_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    game_title = db.Column(db.String(200), nullable=False, index=True)
    user_email = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, added, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<GameRequest {self.game_title} - {self.status}>'
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'game_title': self.game_title,
            'user_email': self.user_email,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }