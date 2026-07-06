import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import routes
from backend.routes import auth_routes, student_routes, faculty_routes, admin_routes

# Initialize FastAPI app
app = FastAPI(
    title="HEI Student Activity Record API",
    description="Centralised Digital Platform for Comprehensive Student Activity Record in HEIs",
    version="1.0.0"
)

# Set up CORS middleware to allow the frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all origins. Can be restricted to local server ports if needed.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads folder exists and is mounted as static files
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(auth_routes.router, prefix="/api")
app.include_router(student_routes.router, prefix="/api")
app.include_router(faculty_routes.router, prefix="/api")
app.include_router(admin_routes.router, prefix="/api")

# API Status Healthcheck
@app.get("/api")
def read_api_root():
    return {
        "status": "online",
        "service": "Centralised Student Activity Record API",
        "documentation": "/docs"
    }

# Serve frontend directory statically at root "/"
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
