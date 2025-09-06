"""
FastAPI application with middleware for AI Arbiter service
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time
import logging
from typing import Optional

from models import HealthResponse, ErrorResponse
from middleware import ArbiterMiddleware, LoggingMiddleware
from services import ArbiterService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Arbiter API",
    description="AI-powered policy arbitration service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(ArbiterMiddleware)

# Initialize services
arbiter_service = ArbiterService()

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            detail="Internal server error",
            error_code="INTERNAL_ERROR",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        ).dict()
    )

# Routes
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint returning service information"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        service="AI Arbiter"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        service="AI Arbiter"
    )

@app.post("/arbitrate")
async def arbitrate_policy(request: Request):
    """
    Main arbitration endpoint that will use the agent service
    This will be expanded to handle policy arbitration requests
    """
    try:
        # Get request data
        request_data = await request.json() if hasattr(request, 'json') else {}
        
        # Use the arbiter service (will be implemented)
        result = await arbiter_service.process_arbitration(request_data)
        
        return {"status": "success", "result": result}
    
    except Exception as e:
        logger.error(f"Error in arbitration: {str(e)}")
        raise HTTPException(status_code=500, detail="Arbitration processing failed")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting AI Arbiter API...")
    await arbiter_service.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AI Arbiter API...")
    await arbiter_service.cleanup()

