from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import csv
import os
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Any, Dict

app = FastAPI()

# Allow CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

QUEUE_FILE = "review_queue.json"
LOG_FILE = "change_log_elfili.csv"
FINAL_OUTPUT_FILE = "elfili_chapter_sentences_NORMALIZED_draft.csv"

# Models
class ReviewAction(BaseModel):
    sentence_id: str
    original_word: str
    proposed_word: str
    final_word: str # what user decided
    action: str # approve, edit, reject, skip
    rule: Optional[str] = None
    timestamp: Optional[str] = None

class QueueUpdate(BaseModel):
    queue: List[Dict[str, Any]]

@app.get("/queue")
def get_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, 'r') as f:
        data = json.load(f)
        return data

@app.post("/log")
def log_action(action: ReviewAction):
    file_exists = os.path.exists(LOG_FILE)
    
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["sentence_id", "original_word", "proposed_word", "final_word", "action", "rule", "timestamp"])
        
        timestamp = action.timestamp or datetime.now().isoformat()
        writer.writerow([
            action.sentence_id,
            action.original_word,
            action.proposed_word,
            action.final_word,
            action.action,
            action.rule,
            timestamp
        ])
    return {"status": "logged"}

@app.post("/save_queue")
def save_queue(update: QueueUpdate):
    # Overwrite queue file with current state so progress persists
    with open(QUEUE_FILE, 'w') as f:
        json.dump(update.queue, f, indent=2)
    return {"status": "saved", "count": len(update.queue)}

@app.post("/export")
def export_session(update: QueueUpdate):
    # Generate the normalized CSV based on current queue state
    # We load original csv structure
    # Update sentences
    # Save to disk
    
    # Not implemented fully yet as queue only contains subset of sentences that have candidates.
    # But queue items contain the FULL sentence segments with changes applied.
    # We need to reconstruct the full text for those sentences.
    
    # For now, just save queue state.
    processed_count = 0
    with open("session_export_queue.json", "w") as f:
        json.dump(update.queue, f)
        
    return {"status": "exported", "message": "Session state exported. Full CSV reconstruction requires merging with original file."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
