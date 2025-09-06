"""
Custom middleware for the AI Arbiter FastAPI application
"""

import time
import logging
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests and responses
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response {request_id}: {response.status_code} "
                f"processed in {process_time:.4f}s"
            )
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            logger.error(
                f"Error {request_id}: {str(e)} "
                f"failed after {process_time:.4f}s"
            )
            raise


class ArbiterMiddleware(BaseHTTPMiddleware):
    """
    Custom middleware for AI Arbiter specific processing
    This middleware will handle agent-related preprocessing and postprocessing
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Preprocessing - prepare request for agent processing
        await self._preprocess_request(request)
        
        # Process request
        response = await call_next(request)
        
        # Postprocessing - handle agent response formatting
        response = await self._postprocess_response(request, response)
        
        return response
    
    async def _preprocess_request(self, request: Request):
        """
        Preprocess requests before they reach the agent service
        """
        # Add metadata for agent processing
        request.state.agent_context = {
            "timestamp": time.time(),
            "user_agent": request.headers.get("user-agent"),
            "content_type": request.headers.get("content-type"),
        }
        
        # Future: Add authentication, rate limiting, input validation
        logger.debug(f"Preprocessing request for agent: {request.url.path}")
    
    async def _postprocess_response(self, request: Request, response: Response) -> Response:
        """
        Postprocess responses from the agent service
        """
        # Add agent-specific headers
        response.headers["X-Agent-Processed"] = "true"
        
        # Future: Add response transformation, caching, metrics
        logger.debug(f"Postprocessing agent response for: {request.url.path}")
        
        return response


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling authentication (placeholder for future implementation)
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Future: Implement JWT token validation, API key authentication, etc.
        # For now, just pass through
        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting (placeholder for future implementation)
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Future: Implement rate limiting logic
        # For now, just pass through
        return await call_next(request)
