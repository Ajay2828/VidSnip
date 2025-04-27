from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi
from sentence_transformers import SentenceTransformer
import chromadb
import uvicorn



# Initialize FastAPI app
app = FastAPI()

# In-memory vector store
chroma_client = chromadb.PersistentClient(path="./chroma")
collection = chroma_client.get_or_create_collection("youtube_transcripts")

# Load embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Define Request/Response Schemas
class LinkRequest(BaseModel):
    youtube_url: str

class QuestionRequest(BaseModel):
    question: str

# Helper to get video_id
def extract_video_id(url):
    import re
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

# Route to process YouTube URL
@app.post("/process_link/")
def process_link(req: LinkRequest):
    video_id = extract_video_id(req.youtube_url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([d["text"] for d in transcript])

        # Split into chunks (very basic splitting)
        chunks = [full_text[i:i+500] for i in range(0, len(full_text), 500)]

        embeddings = embedder.encode(chunks).tolist()

        # Store in Chroma
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=[f"{video_id}-{i}" for i in range(len(chunks))]
        )

        return {"message": "Transcript processed successfully."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Route to answer questions
@app.post("/ask/")
def ask_question(req: QuestionRequest):
    query_embedding = embedder.encode(req.question).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents"]
    )

    relevant_chunks = " ".join([doc for doc in results["documents"][0]])

    # For now, just return relevant chunks (later you can connect to Huggingface LLM to answer properly)
    return {"answer": relevant_chunks}

if __name__ == "__main__":
    uvicorn.run("app", host="0.0.0.0", port=8000, reload=True)
