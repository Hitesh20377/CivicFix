import sys
import os
from datetime import datetime

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'backend'))

from app import create_app
from app.extensions import db
from app.models.issue import IssueCategory

app = create_app()

CATEGORIES = [
    "Road damage",
    "Garbage collection",
    "Broken streetlight",
    "Water leakage",
    "Drainage problem",
    "Traffic signal",
    "Public safety",
    "Other"
]

def seed_categories():
    with app.app_context():
        print("Seeding Issue Categories...")
        for cat_name in CATEGORIES:
            existing = IssueCategory.query.filter_by(name=cat_name).first()
            if not existing:
                cat = IssueCategory(name=cat_name, description=f"Category for {cat_name}", is_active=True)
                db.session.add(cat)
                print(f"Added category: {cat_name}")
            else:
                print(f"Category already exists: {cat_name}")
        db.session.commit()
        print("Done seeding.")

if __name__ == "__main__":
    seed_categories()
