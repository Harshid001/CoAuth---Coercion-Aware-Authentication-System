import requests
import uuid
import random
import time

BACKEND_URL = "http://localhost:3001"

def simulate_bot(bot_type: str):
    session_id = str(uuid.uuid4())
    print(f"--- Simulating {bot_type} ---")
    
    # 1. Create Session
    requests.post(f"{BACKEND_URL}/api/sessions", json={"id": session_id})
    
    # 2. Simulate Interactions based on bot type
    interactions = []
    
    if bot_type == "traditional":
        # Fast, random clicks, no real flow
        for i in range(2):
            requests.post(f"{BACKEND_URL}/api/interactions", json={
                "sessionId": session_id,
                "type": "click",
                "elementId": f"random-link-{i}",
                "url": "/"
            })
            time.sleep(0.1) # Fast!
            
    elif bot_type == "selenium":
        # Hardcoded flow, normal speed
        flow = ["/", "/products/p1", "/cart", "/checkout"]
        for page in flow:
            requests.post(f"{BACKEND_URL}/api/interactions", json={
                "sessionId": session_id,
                "type": "page_view",
                "url": page
            })
            time.sleep(1.5)
            
    elif bot_type == "llm_agent":
        # Realistic flow, slower
        requests.post(f"{BACKEND_URL}/api/interactions", json={"sessionId": session_id, "type": "page_view", "url": "/"})
        time.sleep(2)
        requests.post(f"{BACKEND_URL}/api/interactions", json={"sessionId": session_id, "type": "product_view", "elementId": "product-detail-p3", "url": "/products/p3"})
        time.sleep(4)
        requests.post(f"{BACKEND_URL}/api/interactions", json={"sessionId": session_id, "type": "click", "elementId": "add-to-cart-btn", "url": "/products/p3"})
        time.sleep(1)
        requests.post(f"{BACKEND_URL}/api/interactions", json={"sessionId": session_id, "type": "page_view", "url": "/checkout"})
        time.sleep(2)

    # 3. Request CAPTCHA
    try:
        res = requests.post(f"{BACKEND_URL}/api/captcha/generate", json={"sessionId": session_id})
        challenge = res.json()
        print(f"Received Challenge: {challenge['question']} (Risk: {challenge['difficulty']})")
        
        # 4. Attempt to Solve
        answer = "unknown"
        time_taken = random.randint(500, 3000)
        
        if bot_type == "traditional":
            answer = random.choice(challenge['options']) # Guess randomly
            time_taken = 100 # Instantly
        elif bot_type == "selenium":
            answer = challenge['options'][0] # Dumb hardcoded logic
        elif bot_type == "llm_agent":
            # LLMs might get multiple choice right but fail context recall if they didn't store exactly the product ID
            if challenge['type'] == "multiple_choice":
                answer = "Yes" if "Are you human" in challenge['question'] else "Indigo/Purple" # Basic reasoning
            else:
                answer = random.choice(challenge['options']) # Struggles with visual/context memory unless specifically built for it
        
        verify_res = requests.post(f"{BACKEND_URL}/api/captcha/verify", json={
            "challengeId": challenge['challengeId'],
            "answer": answer,
            "timeTakenMs": time_taken
        })
        print(f"Result: {verify_res.json()}")
    except Exception as e:
        print(f"Error during CAPTCHA flow: {e}")

if __name__ == "__main__":
    for _ in range(5): simulate_bot("traditional")
    for _ in range(5): simulate_bot("selenium")
    for _ in range(5): simulate_bot("llm_agent")
    print("Simulation complete.")
