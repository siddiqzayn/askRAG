from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
import fitz  # PyMuPDF
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

vectorstore = None
rag_chain = None

# -------------------------------
# Upload PDF
# -------------------------------
@app.post("/upload-pdfs/")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    global vectorstore, rag_chain

    if not files:
        return {"error": "No files uploaded!"}

    file_paths = []
    for file in files:
        path = f"temp_{file.filename}"
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file_paths.append(path)

    # Process PDFs
    docs = []
    for path in file_paths:
        pdf = fitz.open(path)
        for page in pdf:
            text = page.get_text()
            if text.strip():
                docs.append(
                    Document(
                        page_content=text,
                        metadata={"page_number": page.number + 1}
                    )
                )

    # Create embeddings & vectorstore
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(docs, embeddings)

    # RAG chain with better retrieval
    llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.3)
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 5}),
        return_source_documents=True,
        chain_type="stuff"
    )

    return {"message": f"✅ Uploaded {len(files)} PDFs and processed {len(docs)} pages"}

# -------------------------------
# Ask Question
# -------------------------------
@app.post("/ask-question/")
async def ask_question(data: dict):
    global rag_chain, vectorstore

    question = data.get("question")
    if not question:
        return {"error": "Question cannot be empty!"}

    # If no PDF uploaded → answer directly with Gemini
    if not rag_chain:
        llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.7)
        response = llm.invoke(question)
        return {"answer": response.content}

    # If PDF uploaded → use RAG with enhanced context
    try:
        result = rag_chain.invoke({"query": question})
        answer = result.get("result", "").strip()
        source_docs = result.get("source_documents", [])

        # If RAG answer is too short or generic, enhance with direct LLM
        if len(answer) < 50 or not answer:
            # Get relevant context from documents
            relevant_docs = vectorstore.similarity_search(question, k=5)
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            # Ask Gemini with context
            llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.3)
            enhanced_prompt = f"""Based on the following context from the document, answer the question accurately and in detail.

Context:
{context}

Question: {question}

Answer:"""
            response = llm.invoke(enhanced_prompt)
            return {"answer": response.content}

        return {"answer": answer}
    
    except Exception as e:
        # Fallback to direct Gemini on error
        llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.7)
        response = llm.invoke(question)
        return {"answer": response.content}

# -------------------------------
# Clear RAG
# -------------------------------
@app.post("/clear-rag/")
async def clear_rag():
    global rag_chain, vectorstore
    rag_chain = None
    vectorstore = None
    return {"message": "✅ RAG cleared"}