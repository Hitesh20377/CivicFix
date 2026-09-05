from datetime import datetime
from pgvector.sqlalchemy import Vector
from ..extensions import db

class TranscriptEmbedding(db.Model):
    """
    Model for storing transcript segment chunks and their semantic vectors.
    """
    __tablename__ = 'transcript_embeddings'
    
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, nullable=False)
    segment_id = db.Column(db.Integer, nullable=True)
    
    speaker = db.Column(db.String(255), nullable=True)
    topic_metadata = db.Column(db.String(255), nullable=True)
    
    start_time = db.Column(db.Float, nullable=True)
    end_time = db.Column(db.Float, nullable=True)
    
    chunk_text = db.Column(db.Text, nullable=False)
    
    # 384 is a common size for smaller transformer models like all-MiniLM-L6-v2
    # Adjust this if using OpenAI (1536) or other providers
    embedding = db.Column(Vector(384))
    
    model_name = db.Column(db.String(100), nullable=True)
    model_version = db.Column(db.String(50), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_transcript_embeddings_meeting', 'meeting_id'),
    )
