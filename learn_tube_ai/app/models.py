# learn_tube_ai/app/models.py

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, JSON, DateTime # Added DateTime
from datetime import datetime, timezone # Keep your datetime import
from typing import Optional # For Optional type hinting

from app import db # Assuming db is initialized in learn_tube_ai/app/__init__.py
from typing import List # For type hinting if you want

class Video(db.Model):
    __tablename__ = 'video' # Explicit table name is good practice

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    video_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True) # Added index
    video_url: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(300), nullable=True) # Increased length for titles
    
    transcript_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transcript_segments: Mapped[Optional[List[dict]]] = mapped_column(JSON, nullable=True) # <<< ADD THIS LINE
    
    # LLM Analysis Fields
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    table_of_contents: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # list of {'title': str, 'timestamp_seconds': int}
    key_terms: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # list of {'term': str, 'definition': str}
    logical_flow: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=lambda: datetime.now(timezone.utc), nullable=True)

    # You could add a relationship here if you had a User model, for example:
    # user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('user.id'), nullable=False)
    # user: Mapped["User"] = relationship(back_populates="videos")

    def __repr__(self):
        return f'<Video id={self.id} video_id={self.video_id}>'

    # Optional: A method to convert model to dictionary, useful for API responses if not handled elsewhere
    def to_dict(self):
        return {
            "id": self.id,
            "video_id": self.video_id,
            "video_url": self.video_url,
            "title": self.title,
            "transcript_text": self.transcript_text,
            "segments": self.transcript_segments or [], # <<< ADD THIS
            "analysis": {
                "summary": self.summary,
                "table_of_contents": self.table_of_contents,
                "key_terms": self.key_terms,
                "logical_flow": self.logical_flow
            },
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# You can add other models here later, for example, a User model:
# class User(db.Model):
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     username: Mapped[str] = mapped_column(String(64), index=True, unique=True)
#     email: Mapped[str] = mapped_column(String(120), index=True, unique=True)
#     videos: Mapped[list["Video"]] = relationship(back_populates="user")