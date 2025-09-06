#!/usr/bin/env python3
"""
Startup script for AI Arbiter FastAPI application
"""

import sys
import os
import asyncio

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def main():
    """Main async function to run the FastAPI application"""
    import uvicorn
    
    # Create uvicorn config
    config = uvicorn.Config(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        

    )
    
    # Create and run the server
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    # Run the FastAPI application with asyncio
    asyncio.run(main())
