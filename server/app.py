import os
import requests
from fastapi import FastAPI, HTTPException, Query
import uvicorn

app = FastAPI()

BASE_URL = os.environ.get('EXTERNAL_SERVICE_BASE_URL', 'https://example.com')

# Helper functions to interact with the external service

def get_exercise_list(username: str):
    """Call external service for exercise list of creator."""
    url = f"{BASE_URL}/get-exercise-list/{username}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_products(username: str):
    """Call external service for products of creator."""
    url = f"{BASE_URL}/get-products/{username}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Tools configuration
TOOLS = {
    "get_exercise_list": {
        "description": "Fetch exercise list for a given creator username.",
        "endpoint": "/tool/get-exercise-list"
    },
    "get_products": {
        "description": "Fetch products for a given creator username.",
        "endpoint": "/tool/get-products"
    }
}

SAMPLE_PROMPTS = [
    "List all exercises created by johndoe using the exercise list tool.",
    "Show me all products by johndoe using the products tool."
]

@app.get('/tools')
def list_tools():
    """Return available tools and sample prompts."""
    return {"tools": TOOLS, "sample_prompts": SAMPLE_PROMPTS}

@app.get('/tool/get-exercise-list')
def tool_exercise_list(username: str = Query(...)):
    try:
        data = get_exercise_list(username)
        return data
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=str(exc))

@app.get('/tool/get-products')
def tool_products(username: str = Query(...)):
    try:
        data = get_products(username)
        return data
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=str(exc))

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)
