# build_knowledge_base.py
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
import re
import os

# Go two levels up from this file → project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Build the correct absolute path to your PDFs
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw", "psychology_books")

print("Looking for PDFs in:", DATA_DIR)

loader = DirectoryLoader(
    DATA_DIR,
    glob="*.pdf",
    loader_cls=PyPDFLoader
)

class AcademicPDFCleaner:
    """Cleans professional/academic PDFs while preserving content integrity"""
    
    def clean_text(self, text: str) -> str:
        """
        Clean academic PDF text while preserving professional content
        Focuses on removing formatting artifacts, not changing content
        """
        if not text:
            return ""
            
        # 1. Remove URLs and hyperlinks
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'\[.*?\]\(.*?\)', '', text)  # Markdown links
        
        # 2. Remove image and figure references
        text = re.sub(r'\[?\b(Figure|Fig\.?|Table|Chart)\s+[A-Za-z0-9\.]+\]?', '', text)
        text = re.sub(r'\(?[Ss]ee\s+[Ff]ig(?:ure)?\.?\s+[A-Za-z0-9\.]+\)?', '', text)
        
        # 3. Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # 4. Remove citation clusters (keep individual citations)
        text = re.sub(r'\([^)]*et al\.[^)]*\)', '', text)  # (Smith et al., 2020; Jones et al., 2021)
        text = re.sub(r'\[[^\]]*et al\.[^\]]*\]', '', text)  # [1-5, 7, 9]
        
        # 5. Clean page headers/footers (common in academic PDFs)
        text = self._remove_repeating_headers(text)
        
        # 6. Remove orphaned characters from PDF extraction
        text = re.sub(r'\s*[•▪♦▶●]\s*', ' ', text)  # Bullet points
        text = re.sub(r'\f', '\n', text)  # Form feeds to newlines
        text = re.sub(r'-\n(\w)', r'\1', text)  # Join hyphenated words across lines
        
        # 7. Normalize whitespace and preserve paragraph structure
        text = re.sub(r'([.!?])\s+', r'\1\n\n', text)  # Sentence endings get double newlines
        text = re.sub(r'\s+', ' ', text)  # Collapse multiple spaces
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Clean paragraph breaks
        
        return text.strip()
    
    def _remove_repeating_headers(self, text: str) -> str:
        """Remove page headers and footers that repeat across pages"""
        lines = text.split('\n')
        cleaned_lines = []
        line_frequency = {}
        
        # Count line frequency
        for line in lines:
            clean_line = line.strip()
            if len(clean_line) > 3:  # Ignore very short lines
                line_frequency[clean_line] = line_frequency.get(clean_line, 0) + 1
        
        # Remove lines that appear too frequently (likely headers/footers)
        threshold = max(3, len(lines) // 20)  # Dynamic threshold
        for line in lines:
            clean_line = line.strip()
            if (line_frequency.get(clean_line, 0) < threshold or 
                len(clean_line) > 60 or  # Long lines are probably content
                any(keyword in clean_line.lower() for keyword in ['abstract', 'introduction', 'method', 'result', 'discussion', 'conclusion'])):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _preserve_citations(self, text: str) -> str:
        """
        Optional: Keep important citations while cleaning format
        """
        # Keep individual author-year citations: (Smith, 2020)
        text = re.sub(r'\(([A-Z][a-z]+,\s*\d{4})\)', r'(\1)', text)
        return text

class KnowledgeBaseBuilder:
    def __init__(self,
                 pdf_directory=DATA_DIR, 
                 persist_directory=os.path.join(PROJECT_ROOT, "data", "outputs", "psychology_books_db_clean")):  # UPDATED PATHS
        self.pdf_directory = pdf_directory
        self.persist_directory = persist_directory
        self.cleaner = AcademicPDFCleaner()

    def build(self):
        print("Step 1: Loading PDFs...")
        loader = DirectoryLoader(self.pdf_directory, glob="**/*.pdf", loader_cls=PyPDFLoader)
        raw_documents = loader.load()
        print(f"Loaded {len(raw_documents)} documents")
    
        print("Step 2: Cleaning academic formatting...")
        cleaned_documents = []
        for i, doc in enumerate(raw_documents):
            cleaned_doc = doc.model_copy()
            original_length = len(cleaned_doc.page_content)
            cleaned_doc.page_content = self.cleaner.clean_text(doc.page_content)
            cleaned_length = len(cleaned_doc.page_content)
        
            # Add metadata about cleaning
            cleaned_doc.metadata = {
                **doc.metadata,
                "cleaned": True,
                "original_chars": original_length,
                "cleaned_chars": cleaned_length,
                "reduction_pct": round((1 - cleaned_length/original_length) * 100, 1) if original_length > 0 else 0
            }
        
            cleaned_documents.append(cleaned_doc)
            print(f"Document {i+1}: {original_length} → {cleaned_length} chars")
    
        print("Step 3: Splitting text into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]  # Preserve paragraph boundaries
        )
        texts = text_splitter.split_documents(cleaned_documents)
        print(f"Created {len(texts)} text chunks")
    
        print("Step 4: Creating embeddings...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
        vector_store = Chroma.from_documents(
            documents=texts,
            embedding=embeddings,
            persist_directory=self.persist_directory
        )
        vector_store.persist()
    
        print("✅ Professional knowledge base built successfully!")
        print(f"📍 Saved to: {self.persist_directory}")
        print(f"📊 Total chunks: {len(texts)}")
    
        # Show cleaning summary
        total_original = sum(doc.metadata.get('original_chars', 0) for doc in cleaned_documents)
        total_cleaned = sum(doc.metadata.get('cleaned_chars', 0) for doc in cleaned_documents)
        avg_reduction = sum(doc.metadata.get('reduction_pct', 0) for doc in cleaned_documents) / len(cleaned_documents)
    
        print(f"🧹 Cleaning summary: {total_original:,} → {total_cleaned:,} chars ({avg_reduction:.1f}% reduction)")

if __name__ == "__main__":
    builder = KnowledgeBaseBuilder()
    builder.build()