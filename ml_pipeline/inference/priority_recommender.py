class PriorityRecommender:
    """Heuristic and keyword-based recommender for Issue Priority."""
    
    SAFETY_KEYWORDS = ['fire', 'sparks', 'blood', 'injury', 'crash', 'danger', 'sinkhole', 'collapse']
    
    @staticmethod
    def recommend(category: str, text: str, user_priority: str):
        text_lower = text.lower()
        score = 0
        reasons = []
        
        # 1. Keyword analysis
        for kw in PriorityRecommender.SAFETY_KEYWORDS:
            if kw in text_lower:
                score += 3
                reasons.append(f"Contains high-risk keyword: '{kw}'")
                
        # 2. Category baseline
        if category in ['Public Safety', 'Electrical']:
            score += 2
            reasons.append(f"Category '{category}' has historically high urgency.")
            
        # 3. User input baseline
        if user_priority == 'CRITICAL':
            score += 1
            reasons.append("Citizen explicitly marked as CRITICAL.")
            
        # Determine recommendation
        if score >= 4:
            suggested = "CRITICAL"
            conf = 0.90
        elif score >= 2:
            suggested = "HIGH"
            conf = 0.75
        elif score >= 1:
            suggested = "MEDIUM"
            conf = 0.60
        else:
            suggested = "LOW"
            conf = 0.80
            reasons.append("No high-risk indicators found.")
            
        return {
            "suggested_priority": suggested,
            "official_priority": user_priority, # We don't overwrite this silently
            "priority_reason": "; ".join(reasons),
            "priority_confidence": conf
        }
