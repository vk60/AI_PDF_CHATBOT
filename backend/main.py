from fastapi.responses import StreamingResponse
from fastapi import FastAPI,UploadFile,File
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from rag import stream_rag,process_pdf
app=FastAPI()
# --------CORS----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)
class QuestionRequest(BaseModel):
    question:str

# -------- UPLOAD FOLDER --------

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)
@app.get("/")
async def home():
    return{
        "message":"AI Background Running"
    }
# -------- PDF UPLOAD --------

@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    file_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    chunks = process_pdf(file_path)

    return {
        "message": "PDF uploaded successfully",
        "chunks": chunks
    }

@app.post("/ask")
async def ask_question(data:QuestionRequest):
     
    
    
    return StreamingResponse(
        stream_rag(data.question),
        media_type="text/plain"
    )