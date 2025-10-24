# Backend API Server
web: cd backend && gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120

# Frontend Build (Vite will serve static files, backend will serve them)
# Railway will detect this and build frontend automatically
