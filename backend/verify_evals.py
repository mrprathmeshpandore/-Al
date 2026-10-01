import json
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def run_test():
    # Setup test DB
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    
    unique_email = f"test_{uuid.uuid4()}@example.com"
    res = client.post("/api/auth/register", json={
        "email": unique_email,
        "password": "Password123!",
        "full_name": "Eval Tester"
    })
    
    if res.status_code != 201:
        print("Signup failed:", res.json())
        return
        
    login_res = client.post("/api/auth/login", json={
        "email": unique_email,
        "password": "Password123!"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    res = client.post("/api/interview/start", headers=headers, json={
        "interview_type": "FULL_INTERVIEW",
        "total_questions": 5
    })
    
    if res.status_code != 201:
        print("Start interview failed:", res.json())
        return
        
    session_id = res.json()["session_id"]
    client.post(f"/api/interview/{session_id}/next-question", headers=headers)
    
    answers = [
        {"name": "Answer A", "text": "AI can improve public service delivery through faster decision-making and better citizen services, but transparency and human oversight are essential."},
        {"name": "Answer B", "text": "I don't think AI should be used extensively in public administration because it can create accountability and privacy concerns."},
        {"name": "Weak Answer", "text": "AI is good. It is useful. It can help government. That's all."}
    ]
    
    results = {}
    
    for ans in answers:
        print(f"--- Testing {ans['name']} ---")
        sub_res = client.post(f"/api/interview/{session_id}/answer", headers=headers, json={
            "answer_text": ans["text"],
            "answer_duration_seconds": 30
        })
        answer_id = sub_res.json()["answer_id"]
        
        eval_res = client.post(f"/api/interview/answers/{answer_id}/evaluate", headers=headers)
        eval_data = eval_res.json()
        
        results[ans["name"]] = {
            "answer_id": answer_id,
            "evaluation_id": eval_data["id"],
            "overall_score": eval_data["overall_score"],
            "feedback": eval_data["overall_feedback"]
        }
        client.post(f"/api/interview/{session_id}/next-question", headers=headers)
        
    print("\n\n--- FINAL EVALUATION RESULTS ---")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    run_test()
