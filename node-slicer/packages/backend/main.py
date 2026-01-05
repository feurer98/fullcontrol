"""
Node-Slicer Backend - FastAPI Application

Visual Node-Editor for creating 3MF files with embedded G-Code for Bambu Lab 3D printers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Node-Slicer API",
    description="Backend API for Node-Slicer - Visual Node-Editor for 3D printing",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Node-Slicer Backend API",
        "version": "0.1.0",
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": "node-slicer-backend",
    }
