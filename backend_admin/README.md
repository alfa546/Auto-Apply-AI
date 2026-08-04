# Admin Portal - Backend

Separate FastAPI backend for admin operations.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your admin credentials
```

4. Run migrations:
```bash
alembic upgrade head
```

5. Start admin backend:
```bash
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## Admin Credentials

Default admin user must be created via CLI:
```bash
python create_admin.py
```

## API Documentation

Once running, visit: http://localhost:8001/docs