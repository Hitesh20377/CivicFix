import os
import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.pipeline import Pipeline
import random

def generate_synthetic_data(num_samples=500):
    np.random.seed(42)
    random.seed(42)
    
    categories = ["Roads/Infrastructure", "Public Safety", "Sanitation", "Electrical", "Water/Plumbing"]
    departments = {
        "Roads/Infrastructure": "Public Works",
        "Public Safety": "Police Department",
        "Sanitation": "Waste Management",
        "Electrical": "Utilities",
        "Water/Plumbing": "Water Board"
    }
    
    priorities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    templates = {
        "Roads/Infrastructure": [
            "There is a huge pothole on {street}.",
            "The sidewalk is cracked near {place}.",
            "Street sign is missing at {street}.",
            "Traffic light is broken at {street}."
        ],
        "Public Safety": [
            "Suspicious activity near {place}.",
            "Vandalism on the wall of {place}.",
            "Broken glass on the playground at {place}.",
            "Streetlights are out, making it dangerous near {street}."
        ],
        "Sanitation": [
            "Garbage not picked up at {street}.",
            "Illegal dumping of trash near {place}.",
            "Dead animal on the road at {street}.",
            "Overflowing public trash can near {place}."
        ],
        "Electrical": [
            "Exposed wires near {place}.",
            "Power outage at {street}.",
            "Sparks flying from transformer near {place}.",
            "Flickering streetlights at {street}."
        ],
        "Water/Plumbing": [
            "Water pipe burst on {street}.",
            "Sewer backing up near {place}.",
            "Fire hydrant leaking at {street}.",
            "No water pressure in buildings near {place}."
        ]
    }
    
    streets = ["Main St", "Elm St", "Oak Ave", "Maple Dr", "Cedar Ln", "Washington Blvd", "Broadway"]
    places = ["Central Park", "High School", "City Hall", "Library", "Downtown Station", "Community Center"]
    
    data = []
    for _ in range(num_samples):
        cat = random.choice(categories)
        template = random.choice(templates[cat])
        text = template.format(
            street=random.choice(streets),
            place=random.choice(places)
        )
        
        # Add some noise to make TF-IDF work a bit harder
        text += " " + " ".join(random.choices(["urgent", "please fix", "dangerous", "annoying", "been here for days"], k=random.randint(0, 2)))
        
        dept = departments[cat]
        
        # Priority logic
        if "dangerous" in text or "sparks" in text or "burst" in text:
            priority = random.choice(["HIGH", "CRITICAL"])
        elif "urgent" in text:
            priority = random.choice(["MEDIUM", "HIGH"])
        else:
            priority = random.choice(["LOW", "MEDIUM"])
            
        # Resolution time logic (hours)
        base_time = {"LOW": 120, "MEDIUM": 72, "HIGH": 24, "CRITICAL": 12}[priority]
        res_time = max(1, np.random.normal(base_time, base_time * 0.2))
        
        data.append({
            "text": text,
            "category": cat,
            "department": dept,
            "priority": priority,
            "resolution_hours": res_time
        })
        
    return pd.DataFrame(data)

def train_and_save():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_registry = os.path.join(base_dir, "..", "model_registry")
    os.makedirs(model_registry, exist_ok=True)
    
    print("Generating synthetic data...")
    df = generate_synthetic_data(1000)
    
    print("Training Category Classifier...")
    cat_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=1000)),
        ('clf', LogisticRegression(random_state=42))
    ])
    cat_pipeline.fit(df['text'], df['category'])
    joblib.dump(cat_pipeline, os.path.join(model_registry, 'category_model_v1.joblib'))
    
    print("Training Department Predictor...")
    dept_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=1000)),
        ('clf', LogisticRegression(random_state=42))
    ])
    dept_pipeline.fit(df['text'], df['department'])
    joblib.dump(dept_pipeline, os.path.join(model_registry, 'department_model_v1.joblib'))
    
    print("Training Priority Predictor...")
    prio_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=1000)),
        ('clf', RandomForestClassifier(n_estimators=50, random_state=42))
    ])
    prio_pipeline.fit(df['text'], df['priority'])
    joblib.dump(prio_pipeline, os.path.join(model_registry, 'priority_model_v1.joblib'))
    
    print("Training Resolution Predictor (Regression)...")
    res_pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=1000)),
        ('reg', RandomForestRegressor(n_estimators=50, random_state=42))
    ])
    res_pipeline.fit(df['text'], df['resolution_hours'])
    joblib.dump(res_pipeline, os.path.join(model_registry, 'resolution_model_v1.joblib'))
    
    print("Saving standalone TF-IDF Vectorizer for Duplicate/Similarity Detection...")
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf.fit(df['text'])
    joblib.dump(tfidf, os.path.join(model_registry, 'tfidf_vectorizer_v1.joblib'))
    
    print("Training complete. Models saved to model_registry.")

if __name__ == "__main__":
    train_and_save()
