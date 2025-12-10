import streamlit as st
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import io

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="🤖 RAG Chatbot", layout="wide")

# -------------------------------
# PDF Generation Function
# -------------------------------
def generate_chat_pdf():
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    question_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=6,
        textColor='blue',
        fontName='Helvetica-Bold'
    )
    answer_style = ParagraphStyle(
        'Answer',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=20,
        leftIndent=20
    )
    
    # Build PDF content
    story = []
    
    # Title
    title = Paragraph("RAG Chatbot Conversation History", title_style)
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Date
    date_text = f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    date_para = Paragraph(date_text, styles['Normal'])
    story.append(date_para)
    story.append(Spacer(1, 20))
    
    # Current chat
    if st.session_state.chat_history:
        current_title = Paragraph("Current Chat Session", styles['Heading2'])
        story.append(current_title)
        story.append(Spacer(1, 12))
        
        for idx, chat in enumerate(st.session_state.chat_history):
            # Question
            q_text = f"Q{idx+1}: {chat['q']}"
            question = Paragraph(q_text, question_style)
            story.append(question)
            
            # Answer
            a_text = f"A{idx+1}: {chat['a']}"
            answer = Paragraph(a_text, answer_style)
            story.append(answer)
    
    # Previous chat sessions
    if st.session_state.chat_sessions:
        for session_idx, session in enumerate(st.session_state.chat_sessions):
            session_title = Paragraph(f"Previous Chat Session {session_idx + 1}", styles['Heading2'])
            story.append(session_title)
            story.append(Spacer(1, 12))
            
            for idx, chat in enumerate(session):
                # Question
                q_text = f"Q{idx+1}: {chat['q']}"
                question = Paragraph(q_text, question_style)
                story.append(question)
                
                # Answer
                a_text = f"A{idx+1}: {chat['a']}"
                answer = Paragraph(a_text, answer_style)
                story.append(answer)
            
            story.append(Spacer(1, 20))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# -------------------------------
# Session State
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = []  # store previous chats

# -------------------------------
# Sidebar: Document Manager (Show only after upload)
# -------------------------------
if st.session_state.uploaded_filename:
    st.sidebar.title("🗁 Document Manager")
    st.sidebar.write(f"**Current PDF:**")
    st.sidebar.write(f"📄 {st.session_state.uploaded_filename}")
    if st.sidebar.button("✘ Clear PDF"):
        st.session_state.uploaded_filename = None
        # Clear RAG on backend
        requests.post(f"{BACKEND_URL}/clear-rag/")
        # Save current chat session
        if st.session_state.chat_history:
            st.session_state.chat_sessions.append(st.session_state.chat_history.copy())
        st.session_state.chat_history = []
        st.rerun()

# -------------------------------
# Page Title with Download Button
# -------------------------------
col1, col2 = st.columns([10, 1])
with col1:
    st.title("✦︎ AskRAG")
with col2:
    if st.session_state.uploaded_filename and (st.session_state.chat_history or st.session_state.chat_sessions):
        st.write("")  # Add spacing
        pdf_buffer = generate_chat_pdf()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}.pdf"
        
        st.download_button(
            label="⬇️",
            data=pdf_buffer,
            file_name=filename,
            mime="application/pdf",
            key="download_pdf",
            help="Download chat as PDF"
        )

# -------------------------------
# Upload Section (Show if no document uploaded)
# -------------------------------
if not st.session_state.uploaded_filename:
    st.markdown("### 🗁 Upload Your Document")
    st.markdown("Upload a PDF document to start chatting with your AI assistant.")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    if uploaded_file is not None:
        with st.spinner("Processing your document..."):
            files = [("files", (uploaded_file.name, uploaded_file.getvalue(), "application/pdf"))]
            response = requests.post(f"{BACKEND_URL}/upload-pdfs/", files=files)
            if response.status_code == 200:
                st.session_state.uploaded_filename = uploaded_file.name
                st.success(f"✅ {uploaded_file.name} uploaded successfully!")
                st.rerun()
            else:
                st.error(f"❌ Upload failed: {response.text}")

# -------------------------------
# Chat Section (Show only after document is uploaded)
# -------------------------------
else:
    # -------------------------------
    # Chat Input
    # -------------------------------
    user_input = st.chat_input("Ask me anything...")
    if user_input:
        response = requests.post(f"{BACKEND_URL}/ask-question/", json={"question": user_input})
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "No answer.")

            st.session_state.chat_history.append({
                "q": user_input,
                "a": answer
            })
        else:
            st.error("Backend error")

    # -------------------------------
    # Display Chat History
    # -------------------------------
    if st.session_state.chat_history:
        st.subheader("💬 Chat History")
        for idx, chat in enumerate(st.session_state.chat_history):
            st.markdown(f"**Q{idx+1}:** {chat['q']}")
            st.markdown(f"**A{idx+1}:** {chat['a']}")
            st.divider()

    # -------------------------------
    # Display Previous Chat Sessions
    # -------------------------------
    if st.session_state.chat_sessions:
        st.subheader("🗂 Previous Chats")
        for i, session in enumerate(st.session_state.chat_sessions):
            with st.expander(f"Session {i+1} ({len(session)} messages)"):
                for idx, chat in enumerate(session):
                    st.markdown(f"**Q{idx+1}:** {chat['q']}")
                    st.markdown(f"**A{idx+1}:** {chat['a']}")
                    st.divider()
