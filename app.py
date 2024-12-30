from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from transformers import pipeline
import os

# Initialiseer de FastAPI-applicatie
app = FastAPI()

# CORS-configuratie
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuratie voor FAISS opslaglocatie
FAISS_DIR = Path("./faiss_store")

# Initialisatie van modellen
class SentenceTransformerWrapper:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts, show_progress_bar=True)

    def embed_query(self, query):
        return self.model.encode([query], show_progress_bar=False)[0]

embeddings_model = SentenceTransformerWrapper()
nlp_pipeline = pipeline("text-generation", model="distilgpt2")  # Lichter model

# FAISS initialisatie
vectorstore = None
if FAISS_DIR.exists():
    vectorstore = FAISS.load_local(str(FAISS_DIR), embeddings_model)

# Helperfunctie om FAISS te laden
def get_vectorstore():
    global vectorstore
    if vectorstore is None:
        if FAISS_DIR.exists():
            vectorstore = FAISS.load_local(str(FAISS_DIR), embeddings_model)
        else:
            raise ValueError("FAISS-bestand niet gevonden. Upload eerst documenten.")
    return vectorstore

# API-endpoints
@app.post("/upload")
async def upload_documents(files: list[UploadFile]):
    """Upload documenten en voeg toe aan de FAISS vectorstore."""
    documents = []

    for file in files:
        content = await file.read()
        texts = content.decode('utf-8').split('\n')
        documents.extend(texts)

    document_texts = [text.strip() for text in documents if text.strip()]

    # Update of maak nieuwe FAISS vectorstore
    global vectorstore
    if vectorstore is None:
        vectorstore = FAISS.from_texts(document_texts, HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))
    else:
        vectorstore.add_texts(document_texts)

    # Sla FAISS op naar bestand
    vectorstore.save_local(str(FAISS_DIR))

    return {"message": f"{len(document_texts)} documenten succesvol geupload en verwerkt."}

@app.post("/kba")
async def answer_question(vraag: str):
    """Beantwoord vragen met behulp van de FAISS vectorstore en een NLP-model."""
    if not vraag:
        raise HTTPException(status_code=400, detail="Geen vraag ontvangen.")

    try:
        vectorstore = get_vectorstore()
        relevante_documenten = vectorstore.similarity_search(vraag, k=3)
        context = "\n".join([doc.page_content for doc in relevante_documenten])

        prompt = (
            f"Gebruik de onderstaande informatie om de vraag te beantwoorden:\n"
            f"{context}\n\n"
            f"Vraag: {vraag}\n"
            f"Antwoord:"
        )

        result = nlp_pipeline(prompt, max_length=200, truncation=True, num_return_sequences=1)
        antwoord = result[0]['generated_text']

        return {"vraag": vraag, "antwoord": antwoord}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interne fout: {str(e)}")

@app.get("/")
async def home():
    """Controleer of de webservice draait."""
    return {"status": "Webservice draait correct!"}