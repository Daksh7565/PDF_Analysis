import google.generativeai as genai
from typing import List, Dict, Any, Generator
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class LLMHandler:
    def __init__(self, provider: str = "gemini"):
        self.provider = provider
        self._setup_client()
    
    def _setup_client(self):
        if self.provider == "gemini":
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(Config.DEFAULT_MODEL)
    
    def generate_response(self, query: str, context: Dict, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """Generate response with citations"""
        context_str = self._format_context(context)
        
        prompt = f"""You are a helpful AI assistant answering questions based on provided PDF documents.
        
Context from documents:
{context_str}

Question: {query}

Instructions:
1. Answer based ONLY on the provided context
2. Cite your sources using [PDF: name, Page: X, Heading: Y] format
3. If the answer isn't in the context, say "I cannot find this information in the provided documents"
4. Be concise but thorough

Provide your answer in this JSON structure:
{{
    "answer": "Your detailed answer here with inline citations [PDF: doc.pdf, Page: 5, Heading: Introduction]",
    "sources": [
        {{
            "pdf_name": "document.pdf",
            "page_number": 5,
            "heading": "Introduction",
            "relevant_text": "Exact text snippet..."
        }}
    ],
    "confidence": "high/medium/low"
}}"""

        try:
            response = self.model.generate_content(prompt)
            raw_text = response.text
            
            clean_json = raw_text.strip().strip('```json').strip('```').strip()
            result = json.loads(clean_json)
            return result
            
        except Exception as e:
            return {
                "answer": raw_text if 'raw_text' in locals() else str(e),
                "sources": [],
                "confidence": "low",
                "error": str(e)
            }
    
    def _format_context(self, context_results: Dict) -> str:
        """Format retrieved context for LLM"""
        formatted = []
        documents = context_results.get('documents', [[]])[0]
        metadatas = context_results.get('metadatas', [[]])[0]
        
        for doc, meta in zip(documents, metadatas):
            ref = f"[PDF: {meta.get('pdf_name', 'Unknown')}, Page: {meta.get('page_number', 'N/A')}, Heading: {meta.get('heading', 'General')}]"
            formatted.append(f"{ref}\n{doc}\n")
        
        return "\n".join(formatted)