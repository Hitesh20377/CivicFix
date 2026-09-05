import pandas as pd
import random
import os

def generate_mock_data(output_path='ml_pipeline/data/mock_issues.csv'):
    categories = ['Road Damage', 'Public Safety', 'Water & Sanitation', 'Electrical', 'Garbage']
    
    # Templates for generating textual data
    templates = {
        'Road Damage': [
            "Massive pothole on {street}, damaging cars.",
            "The road is cracking near {street} intersection.",
            "Sinkhole forming in the middle of {street}."
        ],
        'Public Safety': [
            "Fallen tree blocking {street}.",
            "Suspicious activity near the park on {street}.",
            "Missing stop sign at {street}."
        ],
        'Water & Sanitation': [
            "Water pipe burst flooding {street}.",
            "Sewage backup smelling awful on {street}.",
            "No running water for 3 days on {street}."
        ],
        'Electrical': [
            "Streetlight out for a week on {street}.",
            "Sparking wire dangling over {street}.",
            "Traffic light stuck on red at {street}."
        ],
        'Garbage': [
            "Trash piling up near {street} bins.",
            "Illegal dumping of construction waste on {street}.",
            "Dead animal needs removal from {street}."
        ]
    }
    
    streets = ['Main St', 'Elm St', 'Maple Ave', 'Oak Dr', 'Pine Ln', 'Cedar Blvd']
    
    data = []
    for _ in range(500):
        category = random.choice(categories)
        template = random.choice(templates[category])
        street = random.choice(streets)
        
        text = template.format(street=street)
        data.append({'text': text, 'category': category})
        
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} mock issues at {output_path}")

if __name__ == "__main__":
    generate_mock_data()
