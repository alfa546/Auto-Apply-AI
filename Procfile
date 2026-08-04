# Heroku Procfile - Multiple process types
# Main Backend
web: cd backend && uvicorn src.app.main:app --host 0.0.0.0 --port $PORT

# Admin Backend (separate dyno)
# admin: cd backend_admin && uvicorn main:admin_app --host 0.0.0.0 --port $PORT

# For now, we'll deploy only main backend on Heroku
# Admin portal will be deployed separately or on same dyno with different path