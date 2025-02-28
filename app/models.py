from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    highest_score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    game_sessions = db.relationship('GameSession', backref='player', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def update_highest_score(self, score):
        if score > self.highest_score:
            self.highest_score = score
            db.session.commit()
            return True
        return False

class GameSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Integer, default=0)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    duration = db.Column(db.Integer, default=0)  # in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<GameSession {self.id} - User {self.user_id} - Score {self.score}>'
