"""
API routes - RESTful API endpoints
"""

from flask import Blueprint, request, jsonify
from models import db, Game, GameRequest

api_bp = Blueprint('api', __name__)


@api_bp.route('/games', methods=['GET'])
def get_games():
    """Get all games with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    genre = request.args.get('genre', '')
    
    query = Game.query
    
    if genre:
        query = query.filter_by(genre=genre)
    
    pagination = query.order_by(Game.created_at.desc()).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'games': [game.to_dict() for game in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@api_bp.route('/games/<int:game_id>', methods=['GET'])
def get_game_detail(game_id):
    """Get single game details"""
    game = Game.query.get_or_404(game_id)
    
    # Increment download counter
    game.downloads += 1
    db.session.commit()
    
    return jsonify(game.to_dict()), 200


@api_bp.route('/genres', methods=['GET'])
def get_genres():
    """Get all unique genres"""
    genres = db.session.query(Game.genre).distinct().order_by(Game.genre).all()
    genre_list = [g[0] for g in genres if g[0]]
    return jsonify({'genres': genre_list}), 200


@api_bp.route('/requests', methods=['GET'])
def get_requests():
    """Get game requests"""
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = GameRequest.query
    
    if status:
        query = query.filter_by(status=status)
    
    pagination = query.order_by(GameRequest.created_at.desc()).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'requests': [req.to_dict() for req in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200


@api_bp.route('/search', methods=['GET'])
def search_games():
    """Search games by title or genre"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({'results': []}), 200
    
    games = Game.query.filter(
        (Game.title.ilike(f'%{query}%')) | 
        (Game.description.ilike(f'%{query}%')) |
        (Game.genre.ilike(f'%{query}%'))
    ).limit(20).all()
    
    return jsonify({
        'results': [game.to_dict() for game in games]
    }), 200


@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get platform statistics"""
    total_games = Game.query.count()
    total_downloads = db.session.query(db.func.sum(Game.downloads)).scalar() or 0
    total_requests = GameRequest.query.count()
    pending_requests = GameRequest.query.filter_by(status='pending').count()
    unique_genres = db.session.query(Game.genre).distinct().count()
    
    return jsonify({
        'total_games': total_games,
        'total_downloads': total_downloads,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'unique_genres': unique_genres
    }), 200