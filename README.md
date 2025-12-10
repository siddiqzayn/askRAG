# 🤖 RAG Chatbot

A powerful Retrieval-Augmented Generation (RAG) chatbot that allows you to upload PDF documents and chat with them using AI. Built with FastAPI backend and Streamlit frontend.

## ✨ Features

- 📄 **PDF Upload**: Upload and process PDF documents
- 🤖 **AI Chat**: Ask questions about your documents using Google's Gemini AI
- 💬 **Chat History**: Keep track of all your conversations
- 📥 **Export Chat**: Download chat history as PDF
- 🔄 **Smart Fallback**: Uses both RAG and direct AI for best answers
- 🎨 **Clean UI**: Intuitive interface with document management

## 🛠️ Tech Stack

- **Backend**: FastAPI, LangChain, ChromaDB, PyMuPDF
- **Frontend**: Streamlit, ReportLab
- **AI**: Google Gemini 2.5 Flash
- **Vector Store**: Chroma with HuggingFace embeddings

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd RAG-Chatbot
```

### 2. Set Up Environment Variables
```bash
cd backend
cp .env.example .env
```
Edit `.env` and add your Google API key:
```
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
pip install streamlit requests reportlab
```

### 4. Run the Application

**Start Backend (Terminal 1):**
```bash
cd backend
python -m uvicorn main:app --reload
```

**Start Frontend (Terminal 2):**
```bash
cd frontend
streamlit run app.py
```

### 5. Access the App
- Frontend: http://localhost:8501
- Backend API: http://127.0.0.1:8000

## 📖 How to Use

1. **Upload Document**: Start by uploading a PDF file
2. **Ask Questions**: Type your questions in the chat input
3. **View History**: See all your previous conversations
4. **Download Chat**: Click the ⬇️ button to export chat as PDF
5. **Clear Document**: Use the sidebar to clear and upload new documents

## 🔧 Configuration

### Google API Key Setup
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file

### Environment Variables
- `GOOGLE_API_KEY`: Your Google Gemini API key

## 📁 Project Structure
```
RAG-BOT/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Backend dependencies
│   ├── .env                 # Environment variables (create this)
│   ├── .env.example         # Environment template
│   └── .gitignore          # Git ignore rules
├── frontend/
│   └── app.py              # Streamlit application
├── requirements.txt        # All dependencies
└── README.md              # This file
```

## 🔍 API Endpoints

- `POST /upload-pdfs/`: Upload and process PDF documents
- `POST /ask-question/`: Ask questions about uploaded documents
- `POST /clear-rag/`: Clear the current document and chat history

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Common Issues

**"uvicorn command not found"**
```bash
python -m uvicorn main:app --reload
```

**"Module not found"**
```bash
pip install -r requirements.txt
```

**"API key error"**
- Make sure your `.env` file exists in the backend folder
- Verify your Google API key is correct
- Check that the API key has proper permissions

### Support
If you encounter any issues, please check:
1. All dependencies are installed
2. Environment variables are set correctly
3. Both backend and frontend are running
4. Firewall isn't blocking the ports

---

Made with ❤️ using FastAPI, Streamlit, and Google Gemini AI