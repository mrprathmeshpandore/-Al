import sys
from app.core.database import SessionLocal
from app.services.interview_session_service import InterviewSessionService
from app.models.user import User
import uuid

def run():
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            print("No users in db.")
            return

        service = InterviewSessionService(db)
        session = service.start_interview(user, {
            "interview_type": "FULL_INTERVIEW",
            "total_questions": 5
        })
        print(f"Session started: {session.id}")
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run()
