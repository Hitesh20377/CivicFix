import sys
import os
import joblib
import numpy as np
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity

# Add the project root to python path so we can import the ml_pipeline module if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from app.extensions import db
from app.models.issue import Issue

class MLService:
    _models = {}

    @classmethod
    def load_models(cls):
        """Lazy load all models."""
        if cls._models:
            return
            
        base_dir = os.path.dirname(os.path.abspath(__file__))
        registry_dir = os.path.join(base_dir, '..', '..', '..', 'ml_pipeline', 'model_registry')
        
        try:
            cls._models['category'] = joblib.load(os.path.join(registry_dir, 'category_model_v1.joblib'))
            cls._models['priority'] = joblib.load(os.path.join(registry_dir, 'priority_model_v1.joblib'))
            cls._models['department'] = joblib.load(os.path.join(registry_dir, 'department_model_v1.joblib'))
            cls._models['resolution'] = joblib.load(os.path.join(registry_dir, 'resolution_model_v1.joblib'))
            cls._models['tfidf'] = joblib.load(os.path.join(registry_dir, 'tfidf_vectorizer_v1.joblib'))
        except Exception as e:
            print(f"Warning: Could not load all ML models: {e}")

    @classmethod
    def get_model(cls, name):
        cls.load_models()
        return cls._models.get(name)

    @classmethod
    def triage_issue(cls, title: str, description: str):
        """Returns predictions for category, priority, department, and resolution time."""
        text = f"{title} {description}"
        
        cat_model = cls.get_model('category')
        prio_model = cls.get_model('priority')
        dept_model = cls.get_model('department')
        res_model = cls.get_model('resolution')
        
        results = {
            "model_version": "v1"
        }
        
        if cat_model:
            probs = cat_model.predict_proba([text])[0]
            classes = cat_model.classes_
            class_probs = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)
            results["category"] = class_probs[0][0]
            results["category_confidence"] = float(class_probs[0][1])
            
        if prio_model:
            probs = prio_model.predict_proba([text])[0]
            classes = prio_model.classes_
            class_probs = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)
            results["priority"] = class_probs[0][0]
            results["priority_confidence"] = float(class_probs[0][1])
            
        if dept_model:
            results["department"] = str(dept_model.predict([text])[0])
            
        if res_model:
            results["estimated_resolution_hours"] = float(res_model.predict([text])[0])
            
        return results

    @classmethod
    def find_similar_issues(cls, title: str, description: str, threshold: float = 0.5):
        """Finds potential duplicates or similar historical issues using TF-IDF and Cosine Similarity."""
        text = f"{title} {description}"
        tfidf = cls.get_model('tfidf')
        
        if not tfidf or not text.strip():
            return []
            
        # Get recent issues (e.g., last 1000)
        recent_issues = db.session.query(Issue).order_by(Issue.created_at.desc()).limit(1000).all()
        if not recent_issues:
            return []
            
        issue_texts = [f"{i.title} {i.description}" for i in recent_issues]
        
        # Transform current and historical
        current_vec = tfidf.transform([text])
        history_vecs = tfidf.transform(issue_texts)
        
        # Calculate cosine similarity
        similarities = cosine_similarity(current_vec, history_vecs)[0]
        
        similar_results = []
        for idx, sim in enumerate(similarities):
            if sim >= threshold:
                similar_results.append({
                    "issue_id": recent_issues[idx].id,
                    "title": recent_issues[idx].title,
                    "similarity_score": float(sim),
                    "status": recent_issues[idx].status.name
                })
                
        # Sort by most similar
        similar_results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar_results

    @classmethod
    def attach_predictions_to_issue(cls, issue_id: int, predictions: dict):
        """Attaches the predictions to an existing issue record without mutating official fields."""
        issue = db.session.query(Issue).get(issue_id)
        if not issue:
            return False
            
        issue.suggested_category = predictions.get("category")
        issue.category_confidence = predictions.get("category_confidence")
        
        issue.suggested_priority = predictions.get("priority")
        issue.priority_confidence = predictions.get("priority_confidence")
        
        issue.model_version = predictions.get("model_version")
        
        db.session.commit()
        return True

    @classmethod
    def accept_prediction(cls, issue_id: int):
        """Called by a human when they accept the ML recommendation."""
        issue = db.session.query(Issue).get(issue_id)
        if not issue:
            return False
            
        issue.is_prediction_accepted = True
        db.session.commit()
        return True
