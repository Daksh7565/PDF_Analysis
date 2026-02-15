import streamlit as st
import os
import time
from datetime import datetime

# Must be first Streamlit command
st.set_page_config(
    page_title="PDF Intelligence Hub",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from components.pdf_processor import PDFProcessor
from components.vector_store import VectorStore
from components.llm_handler import LLMHandler
from components.analytics import AnalyticsLogger

# Custom CSS for professional look
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    /* Card styling */
    .stCard {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
    }
    
    /* Chat message styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 0.5rem 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .bot-message {
        background: white;
        color: #333;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 0.5rem 0;
        max-width: 80%;
        float: left;
        clear: both;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    /* Source citation styling */
    .source-box {
        background: #f8f9fa;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 10px 10px 0;
        font-size: 0.9rem;
    }
    
    .source-header {
        color: #28a745;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    /* Upload area styling */
    .upload-area {
        border: 3px dashed #667eea;
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        background: rgba(102, 126, 234, 0.05);
        transition: all 0.3s ease;
    }
    
    .upload-area:hover {
        background: rgba(102, 126, 234, 0.1);
        transform: translateY(-2px);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 30px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #1e1e2e 0%, #2d2d44 100%);
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 10px 10px 0 0;
        padding: 0 2rem;
        font-weight: 600;
    }
    
    /* Header animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animated-header {
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 4px solid #667eea;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .metric-label {
        color: #666;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = VectorStore()
if 'llm_handler' not in st.session_state:
    st.session_state.llm_handler = LLMHandler(provider="gemini")
if 'analytics' not in st.session_state:
    st.session_state.analytics = AnalyticsLogger()
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'processed_pdfs' not in st.session_state:
    st.session_state.processed_pdfs = []
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "upload"

def render_header():
    """Render animated header"""
    st.markdown("""
    <div class="animated-header" style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 3.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                   margin-bottom: 0.5rem;">
            📚 PDF Intelligence Hub
        </h1>
        <p style="color: #666; font-size: 1.2rem;">
            Upload PDFs → Ask Questions → Get Cited Answers
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_upload_section():
    """Render professional upload interface"""
    st.markdown('<div class="upload-area">', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Drop your PDF files here",
        type=["pdf"],
        accept_multiple_files=True,
        help="Supports multiple PDFs up to 800 pages each"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_files:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Process Documents", use_container_width=True):
                process_pdfs(uploaded_files)

def process_pdfs(uploaded_files):
    """Process uploaded PDFs with progress tracking"""
    progress_container = st.container()
    
    with progress_container:
        # Save files temporarily
        pdf_paths = []
        for uploaded_file in uploaded_files:
            save_path = os.path.join(Config.UPLOAD_DIR, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            pdf_paths.append(save_path)
            st.session_state.processed_pdfs.append(uploaded_file.name)
        
        # Process with progress bar
        st.markdown("### 📊 Processing Documents")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        processor = PDFProcessor(max_workers=Config.MAX_WORKERS)
        
        # Simulate progress updates
        total_files = len(pdf_paths)
        for i, pdf_path in enumerate(pdf_paths):
            status_text.text(f"Processing {os.path.basename(pdf_path)}...")
            progress_bar.progress((i + 1) / total_files * 0.5)
        
        # Actual processing
        chunks = processor.process_multiple_pdfs(pdf_paths)
        progress_bar.progress(0.75)
        status_text.text("Creating vector embeddings...")
        
        # Add to vector store
        count = st.session_state.vector_store.add_documents(chunks)
        progress_bar.progress(1.0)
        
        st.success(f"✅ Successfully processed {len(pdf_paths)} PDFs into {count} chunks!")
        time.sleep(1)
        st.session_state.current_tab = "chat"
        st.rerun()

def render_chat_interface():
    """Render professional chat interface"""
    st.markdown("### 💬 Ask Your Documents")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-message">{msg["content"]}</div>', 
                           unsafe_allow_html=True)
            else:
                render_bot_response(msg)
    
    # Input area
    st.markdown("---")
    col1, col2 = st.columns([6, 1])
    with col1:
        query = st.text_input("Ask a question...", key="query_input", 
                             placeholder="e.g., What are the key findings in the introduction?")
    with col2:
        ask_button = st.button("Send", use_container_width=True)
    
    if ask_button and query:
        handle_query(query)

def render_bot_response(msg):
    """Render bot response with citations"""
    response_data = msg.get("response_data", {})
    
    # Main answer
    st.markdown(f'<div class="bot-message">{response_data.get("answer", msg["content"])}</div>', 
               unsafe_allow_html=True)
    
    # Sources section
    sources = response_data.get("sources", [])
    if sources:
        with st.expander("📚 View Sources & References"):
            for source in sources:
                st.markdown(f"""
                <div class="source-box">
                    <div class="source-header">
                        📄 {source.get('pdf_name', 'Unknown')} | Page {source.get('page_number', 'N/A')}
                    </div>
                    <div style="color: #666; font-size: 0.85rem; margin-bottom: 0.5rem;">
                        Heading: {source.get('heading', 'General')}
                    </div>
                    <div style="font-style: italic; color: #555;">
                        "{source.get('relevant_text', 'No preview available')[:200]}..."
                    </div>
                </div>
                """, unsafe_allow_html=True)

def handle_query(query: str):
    """Process query and generate response"""
    start_time = time.time()
    
    # Add user message
    st.session_state.chat_history.append({"role": "user", "content": query})
    
    # Retrieve context
    with st.spinner("🔍 Searching documents..."):
        results = st.session_state.vector_store.query(query, n_results=5)
    
    # Generate response
    with st.spinner("🤖 Generating answer..."):
        response = st.session_state.llm_handler.generate_response(query, results)
    
    response_time = (time.time() - start_time) * 1000
    
    # Add to chat history
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": response.get("answer", ""),
        "response_data": response
    })
    
    # Log analytics
    st.session_state.analytics.log_query(
        query, 
        response,
        {
            "pdf_names": list(set(m.get("pdf_name") for m in results.get("metadatas", [[]])[0])),
            "retrieved_chunks": len(results.get("documents", [[]])[0]),
            "response_time": response_time
        }
    )
    
    st.rerun()

def render_analytics_dashboard():
    """Render analytics dashboard"""
    st.markdown("### 📈 Analytics Dashboard")
    
    stats = st.session_state.analytics.get_analytics()
    
    if not stats:
        st.info("No data available yet. Start chatting to generate analytics!")
        return
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats.get('total_queries', 0)}</div>
            <div class="metric-label">Total Queries</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{stats.get('queries_today', 0)}</div>
            <div class="metric-label">Queries Today</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        feedback = stats.get('feedback_distribution', {})
        total_feedback = feedback.get('thumbs_up', 0) + feedback.get('thumbs_down', 0)
        satisfaction = (feedback.get('thumbs_up', 0) / total_feedback * 100) if total_feedback > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{satisfaction:.0f}%</div>
            <div class="metric-label">Satisfaction Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(st.session_state.processed_pdfs)}</div>
            <div class="metric-label">PDFs Processed</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Most used documents
    st.markdown("### 📚 Most Referenced Documents")
    common_pdfs = stats.get('common_pdfs', {})
    if common_pdfs:
        for pdf, count in sorted(common_pdfs.items(), key=lambda x: x[1], reverse=True)[:5]:
            st.progress(count / max(common_pdfs.values()), text=f"{pdf} ({count} queries)")

def render_sidebar():
    """Render professional sidebar"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: white;">⚙️ Settings</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # LLM Provider selection
        st.markdown("### 🤖 LLM Provider")
        provider = st.selectbox(
            "Choose Provider",
            ["Gemini (Recommended)", "Groq"],
            help="Gemini offers 1M context window for large PDFs"
        )
        
        if provider == "Groq":
            st.session_state.llm_handler = LLMHandler(provider="groq")
        
        # Vector DB Stats
        st.markdown("### 💾 Vector Database")
        stats = st.session_state.vector_store.get_stats()
        st.json(stats)
        
        # Processed files
        if st.session_state.processed_pdfs:
            st.markdown("### 📁 Processed Files")
            for pdf in st.session_state.processed_pdfs:
                st.markdown(f"✅ {pdf}")
        
        # Clear data option
        st.markdown("---")
        if st.button("🗑️ Clear All Data", type="secondary"):
            st.session_state.vector_store.clear()
            st.session_state.processed_pdfs = []
            st.session_state.chat_history = []
            st.success("All data cleared!")
            st.rerun()

def main():
    render_header()
    render_sidebar()
    
    # Navigation tabs
    tabs = st.tabs(["📤 Upload", "💬 Chat", "📊 Analytics"])
    
    with tabs[0]:
        render_upload_section()
    
    with tabs[1]:
        if not st.session_state.processed_pdfs:
            st.warning("👆 Please upload PDFs first in the Upload tab!")
        else:
            render_chat_interface()
    
    with tabs[2]:
        render_analytics_dashboard()

if __name__ == "__main__":
    main()
