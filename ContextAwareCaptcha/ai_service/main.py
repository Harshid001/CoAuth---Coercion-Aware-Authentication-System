from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import random

app = FastAPI()

class Interaction(BaseModel):
    type: str
    url: Optional[str] = None
    elementId: Optional[str] = None
    metadata: Optional[str] = None
    timestamp: str

class CaptchaRequest(BaseModel):
    sessionId: str
    interactions: List[Interaction]

import numpy as np
from sklearn.ensemble import RandomForestClassifier

# Dummy trained model for prototype purposes
# Features: [num_interactions, num_page_views, num_clicks]
# Classes: 0 (Low Risk), 1 (Medium Risk), 2 (High Risk)
X_train = np.array([[20, 10, 10], [10, 5, 5], [2, 1, 1], [1, 1, 0]])
y_train = np.array([0, 1, 2, 2])
clf = RandomForestClassifier(n_estimators=10, random_state=42)
clf.fit(X_train, y_train)

def assess_risk(interactions: List[Interaction]) -> str:
    num_interactions = len(interactions)
    num_page_views = sum(1 for i in interactions if i.type == 'page_view')
    num_clicks = sum(1 for i in interactions if i.type == 'click')
    
    features = np.array([[num_interactions, num_page_views, num_clicks]])
    prediction = clf.predict(features)[0]
    
    if prediction == 0: return "Low"
    elif prediction == 1: return "Medium"
    else: return "High"

@app.post("/generate-captcha")
def generate_captcha(req: CaptchaRequest):
    risk = assess_risk(req.interactions)
    
    # Extract context
    products_viewed = [i.elementId.replace('product-detail-', '') for i in req.interactions if i.type == 'product_view' and i.elementId]
    pages_visited = [i.url for i in req.interactions if i.type == 'page_view' and i.url]
    
    challenge_type = "multiple_choice"
    question = "Are you human?"
    options = ["Yes", "No"]
    answer = "Yes"
    
    if risk == "Low" and products_viewed:
        challenge_type = "context_matching"
        question = "Which of these product IDs did you just view?"
        answer = products_viewed[-1]
        options = [answer, "p99", "p88", "p77"]
        random.shuffle(options)
    elif risk == "Medium" and len(pages_visited) >= 2:
        challenge_type = "sequence"
        question = f"What page were you on before you came to the current page?"
        answer = pages_visited[-2] if len(pages_visited) >= 2 else "/"
        options = ["/", "/cart", "/checkout", "/products/p1"]
        if answer not in options: options[0] = answer
        random.shuffle(options)
    elif risk == "High" or not products_viewed:
        challenge_type = "multiple_choice"
        question = "What is the primary color of the 'Add to Cart' button?"
        options = ["Indigo/Purple", "Red", "Green", "Yellow"]
        answer = "Indigo/Purple"
    
    return {
        "difficulty": risk,
        "type": challenge_type,
        "question": question,
        "options": options,
        "answer": answer
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
