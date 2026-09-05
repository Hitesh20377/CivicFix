import joblib
import os

class CategoryPredictor:
    def __init__(self, model_version="category_model_v1"):
        self.model_version = model_version
        
        # In a real environment, this would be an absolute path or S3 fetch
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, '..', 'model_registry', f'{model_version}.joblib')
        
        try:
            self.model = joblib.load(model_path)
        except Exception as e:
            print(f"Warning: Could not load ML model from {model_path}. Returning fallback.")
            self.model = None

    def predict(self, text: str):
        """Predicts category and returns alternatives with confidences."""
        if not self.model:
            return {
                "predicted_category": "Unknown (Model Not Loaded)",
                "confidence": 0.0,
                "alternatives": [],
                "model_version": "none"
            }
            
        # The pipeline outputs probabilities
        probs = self.model.predict_proba([text])[0]
        classes = self.model.classes_
        
        # Sort by highest probability
        class_probs = sorted(zip(classes, probs), key=lambda x: x[1], reverse=True)
        
        top_category, top_confidence = class_probs[0]
        
        alternatives = [
            {"category": cat, "confidence": round(float(conf), 2)} 
            for cat, conf in class_probs[1:4] if conf > 0.05
        ]
        
        return {
            "predicted_category": top_category,
            "confidence": round(float(top_confidence), 2),
            "alternatives": alternatives,
            "model_version": self.model_version
        }
