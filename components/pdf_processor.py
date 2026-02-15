import pdfplumber
import fitz  # PyMuPDF
import re
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    text: str
    pdf_name: str
    page_number: int
    heading: str
    chunk_id: str
    metadata: Dict[str, Any]


class PDFProcessor:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.heading_pattern = re.compile(r'^(?:Chapter\s+\d+|Section\s+\d+|\d+\.\d+\s+|[A-Z][A-Z\s]{2,}|.{0,50}:)$', re.MULTILINE)
    
    def extract_structure(self, pdf_path: str) -> List[DocumentChunk]:
        """Extract text with structural information"""
        chunks = []
        pdf_name = pdf_path.split("/")[-1].split("\\")[-1]  # Handle both / and \
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    text = page.extract_text() or ""
                    if not text.strip():
                        continue
                    
                    headings = self._extract_headings(text)
                    page_chunks = self._chunk_with_context(
                        text, pdf_name, page_num, headings
                    )
                    chunks.extend(page_chunks)
                    
        except Exception as e:
            print(f"Error processing {pdf_name}: {e}")
            
        return chunks
    
    def _extract_headings(self, text: str) -> List[Dict]:
        """Extract potential headings from text"""
        headings = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if self.heading_pattern.match(line) and len(line) < 100:
                headings.append({
                    "text": line,
                    "line_number": i
                })
        return headings
    
    def _chunk_with_context(self, text: str, pdf_name: str, page_num: int, 
                           headings: List[Dict]) -> List[DocumentChunk]:
        """Create intelligent chunks with metadata"""
        chunks = []
        current_heading = "Introduction/General"
        
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        for i, para in enumerate(paragraphs):
            if any(h["text"] == para for h in headings):
                current_heading = para
                continue
            
            content_hash = hashlib.md5(f"{pdf_name}{page_num}{i}{para[:50]}".encode()).hexdigest()[:12]
            
            chunk = DocumentChunk(
                text=para,
                pdf_name=pdf_name,
                page_number=page_num,
                heading=current_heading,
                chunk_id=content_hash,
                metadata={
                    "char_count": len(para),
                    "word_count": len(para.split()),
                    "position": i
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def process_multiple_pdfs(self, pdf_paths: List[str]) -> List[DocumentChunk]:
        """Process multiple PDFs using ThreadPoolExecutor"""
        all_chunks = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_pdf = {
                executor.submit(self.extract_structure, path): path 
                for path in pdf_paths
            }
            
            for future in as_completed(future_to_pdf):
                pdf_path = future_to_pdf[future]
                try:
                    chunks = future.result()
                    all_chunks.extend(chunks)
                    print(f"Processed {pdf_path}: {len(chunks)} chunks")
                except Exception as e:
                    print(f"Error with {pdf_path}: {e}")
        
        return all_chunks