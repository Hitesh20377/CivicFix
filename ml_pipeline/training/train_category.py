import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

def train():
    data_path = 'ml_pipeline/data/mock_issues.csv'
    if not os.path.exists(data_path):
        print(f"Data not found at {data_path}. Run generate_mock_data.py first.")
        return

    df = pd.read_csv(data_path)
    X = df['text']
    y = df['category']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Baseline Model: TF-IDF + Logistic Regression
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_features=1000)),
        ('clf', LogisticRegression(max_iter=1000, class_weight='balanced'))
    ])
    
    print("Training model...")
    pipeline.fit(X_train, y_train)
    
    print("Evaluating model...")
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    model_dir = 'ml_pipeline/model_registry'
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'category_model_v1.joblib')
    
    joblib.dump(pipeline, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train()
