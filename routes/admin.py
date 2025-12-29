"""
Admin routes - Protected admin dashboard and game management
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, flash
from models import db, Admin, Game, GameRequest
from functools import wraps

admin_bp = Blueprint('admin', __name__)


def login_required(f):
    """Decorator to check if admin is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if 'admin_id' in session:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            return render_template('login.html', error='Username and password required'), 400
        
        admin = Admin.query.filter_by(username=username).first()
        
        if admin and admin.check_password(password):
            session['admin_id'] = admin.id
            session['admin_username'] = admin.username
            return redirect(url_for('admin.dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials'), 401
    
    return render_template('login.html')


@admin_bp.route('/logout')
def logout():
    """Logout admin"""
    session.clear()
    return redirect(url_for('main.index'))


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    admin_id = session.get('admin_id')
    
    # Get admin's games
    games_pagination = Game.query.filter_by(admin_id=admin_id).order_by(
        Game.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    # Get game requests
    requests = GameRequest.query.order_by(GameRequest.created_at.desc()).limit(20).all()
    
    # Get stats
    total_downloads = db.session.query(db.func.sum(Game.downloads)).filter_by(
        admin_id=admin_id
    ).scalar() or 0
    
    return render_template(
        'admin_dashboard.html',
        games=games_pagination.items,
        games_pagination=games_pagination,
        game_requests=requests,
        total_downloads=total_downloads,
        total_games=games_pagination.total,
        total_requests=GameRequest.query.count()
    )


@admin_bp.route('/api/game/add', methods=['POST'])
@login_required
def add_game():
    """Add new game"""
    try:
        data = request.get_json()
        admin_id = session.get('admin_id')
        
        # Validate input
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        genre = data.get('genre', '').strip()
        cover_image_url = data.get('cover_image_url', '').strip()
        download_link = data.get('download_link', '').strip()
        
        if not all([title, description, genre, cover_image_url, download_link]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        if len(title) < 2:
            return jsonify({'success': False, 'message': 'Title too short'}), 400
        
        # Check if game already exists
        existing = Game.query.filter_by(title=title).first()
        if existing:
            return jsonify({'success': False, 'message': 'Game already exists'}), 400
        
        # Create game
        game = Game(
            title=title,
            description=description,
            genre=genre,
            cover_image_url=cover_image_url,
            download_link=download_link,
            admin_id=admin_id
        )
        
        db.session.add(game)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Game "{title}" added successfully!',
            'game': game.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@admin_bp.route('/api/game/<int:game_id>/update', methods=['PUT'])
@login_required
def update_game(game_id):
    """Update game"""
    try:
        game = Game.query.get_or_404(game_id)
        
        # Verify ownership
        if game.admin_id != session.get('admin_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        if 'title' in data:
            game.title = data['title'].strip()
        if 'description' in data:
            game.description = data['description'].strip()
        if 'genre' in data:
            game.genre = data['genre'].strip()
        if 'cover_image_url' in data:
            game.cover_image_url = data['cover_image_url'].strip()
        if 'download_link' in data:
            game.download_link = data['download_link'].strip()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Game updated successfully!',
            'game': game.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@admin_bp.route('/api/game/<int:game_id>/delete', methods=['DELETE'])
@login_required
def delete_game(game_id):
    """Delete game"""
    try:
        game = Game.query.get_or_404(game_id)
        
        # Verify ownership
        if game.admin_id != session.get('admin_id'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        title = game.title
        db.session.delete(game)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Game "{title}" deleted successfully!'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500


@admin_bp.route('/api/request/<int:request_id>/update', methods=['PUT'])
@login_required
def update_request(request_id):
    """Update game request status"""
    try:
        game_request = GameRequest.query.get_or_404(request_id)
        data = request.get_json()
        
        status = data.get('status', '').lower()
        if status not in ['pending', 'added', 'rejected']:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        
        game_request.status = status
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Request status updated to {status}!',
            'request': game_request.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500