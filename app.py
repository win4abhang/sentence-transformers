from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
import uvicorn
import os

# Load the MiniLM model with caching
model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=".cache")

# Initialize FastAPI app
app = FastAPI()

# Predefined intent tags and labels (inline instead of CSV)
intent_tags = {
    "puncture": "Bike Repair",
    "bike repair": "Bike Repair",
    "tyre change": "Bike Repair",
    "haircut": "Salon",
    "grocery": "Grocery Store",
    "vegetables": "Grocery Store",
    "medicine": "Medical Store",
    "doctor": "Healthcare",
    "tuition": "Education",
    "plumber": "Home Services",
    "electrician": "Home Services"
}

# Precompute embeddings for each intent label
tag_embeddings = {
    tag: model.encode(tag, convert_to_tensor=True)
    for tag in intent_tags
}

# Define input schema
class QueryInput(BaseModel):
    query: str

# API endpoint to return best-matching intent
@app.post("/intent")
def get_intent(input: QueryInput):
    query_embedding = model.encode(input.query, convert_to_tensor=True)

    best_match = None
    best_score = -1

    for tag_text, tag_embedding in tag_embeddings.items():
        score = util.cos_sim(query_embedding, tag_embedding).item()
        if score > best_score:
            best_score = score
            best_match = tag_text

    return {
        "intent": intent_tags[best_match],
        "matched_text": best_match,
        "confidence": round(best_score, 3)
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
