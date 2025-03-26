from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

try:
    from email_classification import VALID_CATEGORIES, SUBTYPE_MAPPING  # Import from external file
except ModuleNotFoundError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from config import VALID_CATEGORIES, SUBTYPE_MAPPING

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust based on frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequestType(BaseModel):
    requestType: str
    subRequestType: List[str] = []

@app.get("/categories")
def get_categories():
    """Returns available categories, mapping to subtypes if available."""
    result = [
        {
            "id": idx + 1,
            "requestType": category,
            "subRequestType": SUBTYPE_MAPPING.get(category, ["N/A"])
        }
        for idx, category in enumerate(VALID_CATEGORIES)
    ]
    return {"categories": result}

@app.post("/add-category")
def add_category(request: RequestType):
    """Adds a new request type and subrequest types."""
    existing_subrequests = SUBTYPE_MAPPING.get(request.requestType, [])

    # Check if request type exists with the same subrequest types
    if request.requestType in VALID_CATEGORIES and set(request.subRequestType) <= set(existing_subrequests):
        raise HTTPException(status_code=400, detail="This request type with the same sub-request types already exists.")

    # If request type exists, update sub-request types
    if request.requestType in VALID_CATEGORIES:
        SUBTYPE_MAPPING[request.requestType] = list(set(existing_subrequests + request.subRequestType))
    else:
        VALID_CATEGORIES.add(request.requestType)
        SUBTYPE_MAPPING[request.requestType] = request.subRequestType if request.subRequestType else ["N/A"]

    return {"message": "Category added successfully", "categories": {cat: SUBTYPE_MAPPING.get(cat, ["N/A"]) for cat in VALID_CATEGORIES}}


# Run FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
