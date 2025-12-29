"""
Main routes - Public routes for landing page and game search
"""

from flask import Blueprint, render_template, request, jsonify
from models import db, Game, GameRequest
from sqlalchemy import func
import re

main_bp = Blueprint('main', __name__)


def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@main_bp.route('/')
def index():
    """Landing page"""
    # Get featured games (10 most recent)
    featured_games = Game.query.order_by(Game.created_at.desc()).limit(10).all()
    
    return render_template('landing.html', games=featured_games)


@main_bp.route('/search')
def search():
    """Search games"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'results': []})
    
    # Search in title and description
    games = Game.query.filter(
        (Game.title.ilike(f'%{query}%')) | 
        (Game.description.ilike(f'%{query}%'))
    ).limit(20).all()
    
    results = [game.to_dict() for game in games]
    return jsonify({'results': results})


@main_bp.route('/api/games/<int:game_id>')
def get_game(game_id):
    """Get game details"""
    game = Game.query.get_or_404(game_id)
    return jsonify(game.to_dict())


@main_bp.route('/request-game', methods=['POST'])
def request_game():
    """Handle game request from user"""
    try:
        data = request.get_json()
        
        # Validate input
        game_title = data.get('game_title', '').strip()
        user_email = data.get('user_email', '').strip()
        
        if not game_title or len(game_title) < 2:
            return jsonify({'success': False, 'message': 'Game title is required'}), 400
        
        if user_email and not is_valid_email(user_email):
            return jsonify({'success': False, 'message': 'Invalid email address'}), 400
        
        # Check if game already exists
        existing_game = Game.query.filter(
            func.lower(Game.title) == func.lower(game_title)
        ).first()
        
        if existing_game:
            return jsonify({
                'success': False, 
                'message': f'Game "{game_title}" is already available!'
            }), 400
        
        # Check if request already exists
        existing_request = GameRequest.query.filter(
            func.lower(GameRequest.game_title) == func.lower(game_title)
        ).first()
        
        if existing_request:
            return jsonify({
                'success': False, 
                'message': f'Request for "{game_title}" already exists'
            }), 400
        
        # Create new request
        game_request = GameRequest(
            game_title=game_title,
            user_email=user_email or None,
            status='pending'
        )
        
        db.session.add(game_request)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Request for "{game_title}" submitted successfully! Admin will review it.'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False, 
            'message': f'Error submitting request: {str(e)}'
        }), 500


@main_bp.route('/api/stats')
def get_stats():
    """Get platform statistics"""
    total_games = Game.query.count()
    total_requests = GameRequest.query.count()
    pending_requests = GameRequest.query.filter_by(status='pending').count()
    
    return jsonify({
        'total_games': total_games,
        'total_requests': total_requests,
        'pending_requests': pending_requests
    })