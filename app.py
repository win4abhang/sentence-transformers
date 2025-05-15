from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
import csv
import uvicorn
import os

model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder=".cache")

# Initialize FastAPI app
app = FastAPI()

# Load the MiniLM model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Predefined intent tags and labels
intent_tags = {}
base_dir = os.path.dirname(__file__)
csv_path = os.path.join(base_dir, "intent_tags.csv")
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        intent_tags[row['tag']] = row['label']

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