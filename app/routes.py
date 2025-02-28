from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app import db
from app.models import User, GameSession
from app.game import MathGame
from datetime import datetime, date
import json

bp = Blueprint('main', __name__)
game = MathGame()

@bp.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            # Check if user exists
            user = User.query.filter_by(username=username).first()
            if not user:
                # Create new user
                user = User(username=username)
                db.session.add(user)
                db.session.commit()
            
            session['user_id'] = user.id
            return redirect(url_for('main.welcome'))
    
    # Check if user is already logged in
    if 'user_id' in session:
        return redirect(url_for('main.welcome'))
        
    return render_template('home.html')

@bp.route('/welcome')
def welcome():
    if 'user_id' not in session:
        return redirect(url_for('main.home'))
    
    user = User.query.get(session['user_id'])
    
    # Get daily leaderboard
    today = date.today()
    daily_leaders = db.session.query(
        User.username, 
        db.func.max(GameSession.score).label('max_score')
    ).join(GameSession).filter(
        GameSession.date == today
    ).group_by(User.username).order_by(
        db.desc('max_score')
    ).limit(10).all()
    
    return render_template('welcome.html', user=user, leaderboard=daily_leaders)

@bp.route('/game')
def game_page():
    if 'user_id' not in session:
        return redirect(url_for('main.home'))
    
    # Reset game state
    session['game_level'] = 1
    session['game_score'] = 0
    session['game_start_time'] = datetime.utcnow().timestamp()
    
    return render_template('game.html')

@bp.route('/api/equation', methods=['GET'])
def get_equation():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    level = session.get('game_level', 1)
    game.current_level = level
    
    equation_data = game.generate_equation()
    return jsonify(equation_data)

@bp.route('/api/answer', methods=['POST'])
def check_answer():
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.json
    user_answer = data.get('is_correct')
    actual_correct = data.get('actual_correct')
    
    if user_answer == actual_correct:
        # Correct answer
        session['game_score'] = session.get('game_score', 0) + 1
        session['game_level'] = session.get('game_level', 1) + 1
        
        return jsonify({
            "correct": True,
            "score": session['game_score'],
            "level": session['game_level']
        })
    else:
        # Wrong answer - game over
        score = session.get('game_score', 0)
        user_id = session['user_id']
        
        # Calculate duration
        start_time = session.get('game_start_time', datetime.utcnow().timestamp())
        duration = int(datetime.utcnow().timestamp() - start_time)
        
        # Save game session
        game_session = GameSession(
            user_id=user_id,
            score=score,
            duration=duration
        )
        db.session.add(game_session)
        
        # Update user's highest score if needed
        user = User.query.get(user_id)
        user.update_highest_score(score)
        
        db.session.commit()
        
        return jsonify({
            "correct": False,
            "score": score,
            "highest_score": user.highest_score
        })

@bp.route('/game_over')
def game_over():
    if 'user_id' not in session:
        return redirect(url_for('main.home'))
    
    user = User.query.get(session['user_id'])
    score = session.get('game_score', 0)
    
    # Get daily leaderboard
    today = date.today()
    daily_leaders = db.session.query(
        User.username, 
        db.func.max(GameSession.score).label('max_score')
    ).join(GameSession).filter(
        GameSession.date == today
    ).group_by(User.username).order_by(
        db.desc('max_score')
    ).limit(10).all()
    
    return render_template('game_over.html', 
                          user=user, 
                          score=score, 
                          leaderboard=daily_leaders)

@bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main.home'))
