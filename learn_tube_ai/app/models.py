from . import db # Import the db instance from app/__init__.py
from datetime import datetime, timezone

class Video(db.Model):
    __tablename__ = 'video'

    id = db.Column(db.String(11), primary_key=True) # YouTube video ID (e.g., dQw4w9WgXcQ)
    title = db.Column(db.String(255), nullable=True) # We might not always fetch this initially
    
    # Storing large text fields
    transcript_text = db.Column(db.Text, nullable=True)
    
    # Storing JSON data
    # For SQLite, JSON is often stored as TEXT. For PostgreSQL, db.JSON is better.
    # Using db.Text for broader compatibility initially.
    llm_analysis_json = db.Column(db.Text, nullable=True) # Store the JSON string from LLM

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Process status
    # 'pending', 'processing_transcript', 'processing_llm', 'completed', 'failed_transcript', 'failed_llm'
    processing_status = db.Column(db.String(50), nullable=True, default='pending')
    last_processing_error = db.Column(db.Text, nullable=True)


    def __repr__(self):
        return f'<Video {self.id} - {self.title or "N/A"}>'

    def to_dict(self):
        """Returns a dictionary representation of the video, useful for API responses."""
        return {
            'video_id': self.id,
            'title': self.title,
            # transcript_text might be too large for general to_dict, handle separately if needed
            'llm_analysis': self.get_llm_analysis(), # Use a helper to parse JSON
            'processing_status': self.processing_status,
            'last_processing_error': self.last_processing_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_llm_analysis(self):
        """Parses the llm_analysis_json string into a Python dict."""
        if self.llm_analysis_json:
            import json
            try:
                return json.loads(self.llm_analysis_json)
            except json.JSONDecodeError:
                return {"error": "Failed to parse stored LLM analysis."}
        return None

    def set_llm_analysis(self, analysis_dict):
        """Converts a Python dict into a JSON string for storage."""
        if analysis_dict:
            import json
            self.llm_analysis_json = json.dumps(analysis_dict)
        else:
            self.llm_analysis_json = None