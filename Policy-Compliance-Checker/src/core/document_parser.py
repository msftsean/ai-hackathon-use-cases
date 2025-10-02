"""
Policy Compliance Checker - Core Document Parser
Handles parsing of various document formats and extracting text content.
"""
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import pypdf
from docx import Document
import json
import re
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PolicyDocument:
    """Represents a parsed policy document"""
    title: str
    content: str
    document_type: str
    file_path: str
    metadata: Dict[str, Any]
    sections: List[Dict[str, str]]
    created_at: datetime


class DocumentParser:
    """Handles parsing of various document formats"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt', '.md']
    
    def parse_document(self, file_path: str) -> PolicyDocument:
        """Parse a document and return a PolicyDocument object"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        # Extract content based on file type
        if file_extension == '.pdf':
            content = self._parse_pdf(file_path)
        elif file_extension == '.docx':
            content = self._parse_docx(file_path)
        elif file_extension in ['.txt', '.md']:
            content = self._parse_text(file_path)
        else:
            raise ValueError(f"Unsupported format: {file_extension}")
        
        # Extract metadata and sections
        title = self._extract_title(content, file_path)
        sections = self._extract_sections(content)
        metadata = self._extract_metadata(content, file_path)
        
        return PolicyDocument(
            title=title,
            content=content,
            document_type=file_extension,
            file_path=file_path,
            metadata=metadata,
            sections=sections,
            created_at=datetime.now()
        )
    
    def _parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = pypdf.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise ValueError(f"Error parsing PDF {file_path}: {str(e)}")
    
    def _parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error parsing DOCX {file_path}: {str(e)}")
    
    def _parse_text(self, file_path: str) -> str:
        """Extract text from plain text or markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise ValueError(f"Error parsing text file {file_path}: {str(e)}")
    
    def _extract_title(self, content: str, file_path: str) -> str:
        """Extract document title from content or filename"""
        # Try to find title in first few lines
        lines = content.split('\n')[:5]
        for line in lines:
            line = line.strip()
            # Look for markdown headers or short lines that look like titles
            if line and line.startswith('#'):
                return line.replace('#', '').strip()
            # Look for short lines that could be titles (but not regular sentences)
            elif line and len(line.split()) <= 6 and not line.endswith('.') and not line.lower().startswith(('some', 'this', 'the')):
                return line.strip()
        
        # Fallback to filename
        return Path(file_path).stem.replace('_', ' ').replace('-', ' ').title()
    
    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """Extract sections from document content"""
        sections = []
        
        # Simple section detection using headers
        lines = content.split('\n')
        current_section = {"title": "Introduction", "content": ""}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect headers (lines starting with #, or all caps, or numbered)
            if (line.startswith('#') or 
                line.isupper() or 
                re.match(r'^\d+\.', line) or
                re.match(r'^[A-Z][A-Z\s]+$', line)):
                
                # Save previous section if it has content
                if current_section["content"].strip():
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    "title": line.replace('#', '').strip(),
                    "content": ""
                }
            else:
                current_section["content"] += line + "\n"
        
        # Add final section
        if current_section["content"].strip():
            sections.append(current_section)
        
        return sections
    
    def _extract_metadata(self, content: str, file_path: str) -> Dict[str, Any]:
        """Extract metadata from document"""
        metadata = {
            "file_size": os.path.getsize(file_path),
            "word_count": len(content.split()),
            "character_count": len(content),
            "line_count": len(content.split('\n')),
            "file_extension": Path(file_path).suffix
        }
        
        # Look for dates in content
        date_patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b\w+ \d{1,2}, \d{4}\b'
        ]
        
        dates_found = []
        for pattern in date_patterns:
            matches = re.findall(pattern, content)
            dates_found.extend(matches)
        
        if dates_found:
            metadata["dates_mentioned"] = dates_found[:5]  # First 5 dates
        
        return metadata