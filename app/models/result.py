# backend/app/models/result.py
from app.extensions import db
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSONB

class Result(db.Model):
    __tablename__ = 'results'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(JSONB, nullable=False)
    theme = db.Column(db.String(50), nullable=False)
    focus = db.Column(db.String(50), nullable=False)
    foto = db.Column(db.String(255), nullable=True) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref=db.backref('results', lazy=True))

    def __repr__(self):
        return f"<Result {self.id} - Theme: {self.theme}, Focus: {self.focus}>"