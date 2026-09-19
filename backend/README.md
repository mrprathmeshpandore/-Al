# Prashasak AI — Backend (FastAPI + PostgreSQL Foundation)

This is the backend API service for **Prashasak AI — तयारी विचारांची, उद्याच्या भारतासाठी.**

## Tech Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Server**: Uvicorn

## Setup & Running

### 1. Create Virtual Environment & Install Dependencies
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # On Windows
pip install -r requirements.txt
```

### 2. Environment Variables
Copy `.env.example` to `.env` and fill in your database credentials:
```bash
cp .env.example .env
```

### 3. Run Database Migrations
```bash
alembic upgrade head
```

### 4. Start Local Development Server
```bash
uvicorn app.main:app --reload
```
Server runs at: `http://127.0.0.1:8000`  
Interactive Swagger Docs: `http://127.0.0.1:8000/docs`

### 5. Running Tests
```bash
pytest
```
