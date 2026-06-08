from sentence_transformers import  SentenceTransformer
from database import collection
from pypdf import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import uuid

# -----------LOAD ENV-----------------
load_dotenv()

# -----------Gemini config-------------

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ---------GENAI MODEL------------------

model=genai.GenerativeModel("models/gemini-2.5-flash")

# -------Embedding model-----------------
embedding_model=SentenceTransformer("all-MiniLM-l6-v2")

# ------PDF PROCESSING---------------------

def process_pdf(pdf_path):

    reader = PdfReader(pdf_path)

    text = ""

    # Extract text from all pages
    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted

    print("TEXT EXTRACTED")

    # -------- TEXT SPLITTING --------

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = text_splitter.split_text(text)

    print("TOTAL CHUNKS:", len(chunks))

    # -------- CREATE EMBEDDINGS --------

    embeddings = embedding_model.encode(
        chunks
    ).tolist()

    ids = [
        str(uuid.uuid4())
        for _ in chunks
    ]

    # -------- STORE IN CHROMADB --------

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids
    )

    print("DATA STORED")

    return len(chunks)

# ------Rag function---------
def stream_rag(question):
    # create question embedding-------
    query_embedding=embedding_model.encode(question)

    # ---Vector search CHROMODB-----------------
    result=collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=3
    )
    # ------EXTRACT DOCUMENTS--------------
    documents=result["documents"][0]

    # -------Create Context----------------

    context="\n".join(documents)
    if not context.strip():
        yield "I could not find this information"
        return

    # --------Prompt-----------------------

    prompt=f""" 
    You are an intelligent AI assistant.

    Answer ONLY from the provided context.

    If answer is not available,
    say:
    "I could not find this information."

    Context:
    {context}

    Question:
    {question}

    """ 

    # --------Gimini Response------------

    response=model.generate_content(prompt,stream=True)
   
#    ------YEILD TOKENS------------------
    for chunk in response:
       if chunk.text:
        yield chunk.text