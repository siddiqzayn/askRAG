from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
import fitz  # PyMuPDF
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.schema import Document

# ✅ Your Google API key (hardcoded for now)
GOOGLE_API_KEY = "AIzaSyDLIFIYCPwNFCYP5wrMfzKp4INmecoGYk4"

app = FastAPI()

# Allow CORS
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
                        metadata={"page_number": page.number + 1}  # actual PDF page
                    )
                )

    # Create embeddings & vectorstore
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)
    vectorstore = Chroma.from_documents(docs, embeddings)

    # RAG chain
    llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", google_api_key=GOOGLE_API_KEY)
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 2}),
        return_source_documents=True,
    )

    return {"message": f"✅ Uploaded {len(files)} PDFs and processed {len(docs)} pages"}

# -------------------------------
# Ask Question
# -------------------------------
@app.post("/ask-question/")
async def ask_question(data: dict):
    global rag_chain

    question = data.get("question")
    if not question:
        return {"error": "Question cannot be empty!"}

    # If no PDF uploaded → answer directly with Gemini
    if not rag_chain:
        llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", google_api_key=GOOGLE_API_KEY)
        response = llm.invoke(question)
        return {"answer": response.content, "sources": []}

    # If PDF uploaded → use RAG
    result = rag_chain.invoke({"query": question})
    answer = result.get("result", "No answer found.")
    sources = [f"📄 Page {doc.metadata.get('page_number')}" for doc in result.get("source_documents", [])]

    return {"answer": answer, "sources": sources}
