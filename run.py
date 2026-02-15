#Starts your FastAPI server
import uvicorn
import os
import sys

# Make sure Python finds all project modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="localhost",
        port=8000,
        reload=True
    )
