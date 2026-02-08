#!/usr/bin/env python3
"""PDF File Store Manager - handles PDF storage and extraction from doc_dump folder.

This module provides utilities for managing PDF files in the doc_dump folder,
including file discovery, extraction, and metadata tracking.
"""

from pathlib import Path
from typing import List, Optional, Dict
import logging
import shutil
from datetime import datetime


class PDFFileStore:
    """Manages PDF files stored in the doc_dump directory."""
    
    def __init__(self, doc_dump_dir: Optional[str] = None):
        """Initialize the PDF FileStore.
        
        Args:
            doc_dump_dir: Path to doc_dump directory. If None, uses ./doc_dump relative to script.
        """
        if doc_dump_dir is None:
            # Default to doc_dump folder in the same directory as this script
            script_dir = Path(__file__).parent
            doc_dump_dir = str(script_dir / "doc_dump")
        
        self.doc_dump_path = Path(doc_dump_dir).expanduser()
        self.extracted_dir = self.doc_dump_path.parent / "extracted_pdfs"
        
        # Create directories if they don't exist
        self.doc_dump_path.mkdir(parents=True, exist_ok=True)
        self.extracted_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)
    
    def get_all_pdfs(self) -> List[Path]:
        """Get all PDF files in doc_dump directory.
        
        Returns:
            List of Path objects for all PDFs found.
        """
        if not self.doc_dump_path.exists():
            self.logger.warning(f"doc_dump directory not found at {self.doc_dump_path}")
            return []
        
        pdfs = list(self.doc_dump_path.glob("*.pdf"))
        self.logger.info(f"Found {len(pdfs)} PDF(s) in {self.doc_dump_path}")
        return pdfs
    
    def get_pdf_info(self, pdf_path: Path) -> Dict:
        """Get metadata about a PDF file.
        
        Args:
            pdf_path: Path to the PDF file.
            
        Returns:
            Dictionary with PDF metadata.
        """
        if not pdf_path.exists():
            return {}
        
        stat = pdf_path.stat()
        return {
            "filename": pdf_path.name,
            "path": str(pdf_path),
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
        }
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Optional[str]:
        """Extract text from PDF file.
        
        Args:
            pdf_path: Path to the PDF file.
            
        Returns:
            Extracted text or None if extraction fails.
        """
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            self.logger.error("PyPDF2 not installed. Install with: pip install PyPDF2")
            return None
        
        try:
            reader = PdfReader(str(pdf_path))
            text_parts = []
            
            for page_num, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text:
                        text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
                except Exception as e:
                    self.logger.warning(f"Error extracting page {page_num + 1}: {e}")
                    continue
            
            extracted_text = "\n\n".join(text_parts)
            self.logger.info(f"Successfully extracted text from {pdf_path.name}")
            return extracted_text
        
        except Exception as e:
            self.logger.error(f"Failed to extract text from {pdf_path.name}: {e}")
            return None
    
    def save_extracted_text(self, pdf_path: Path, text: str) -> Optional[Path]:
        """Save extracted text to a .txt file.
        
        Args:
            pdf_path: Path to the PDF file.
            text: Extracted text content.
            
        Returns:
            Path to the saved text file or None if save fails.
        """
        try:
            txt_path = self.extracted_dir / pdf_path.stem / f"{pdf_path.stem}.txt"
            txt_path.parent.mkdir(parents=True, exist_ok=True)
            txt_path.write_text(text, encoding="utf-8")
            self.logger.info(f"Saved extracted text to {txt_path}")
            return txt_path
        except Exception as e:
            self.logger.error(f"Failed to save extracted text: {e}")
            return None
    
    def copy_pdf(self, pdf_path: Path, dest_subdir: Optional[str] = None) -> Optional[Path]:
        """Copy a PDF file to extracted_pdfs directory.
        
        Args:
            pdf_path: Path to the PDF file.
            dest_subdir: Optional subdirectory name for organization.
            
        Returns:
            Path to the copied file or None if copy fails.
        """
        try:
            if dest_subdir:
                dest_dir = self.extracted_dir / dest_subdir
            else:
                dest_dir = self.extracted_dir / pdf_path.stem
            
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / pdf_path.name
            shutil.copy2(str(pdf_path), str(dest_path))
            self.logger.info(f"Copied {pdf_path.name} to {dest_path}")
            return dest_path
        except Exception as e:
            self.logger.error(f"Failed to copy PDF: {e}")
            return None
    
    def process_all_pdfs(self, extract_text: bool = True) -> Dict:
        """Process all PDFs in doc_dump folder.
        
        Args:
            extract_text: Whether to extract text from PDFs.
            
        Returns:
            Dictionary with processing results.
        """
        pdfs = self.get_all_pdfs()
        results = {
            "total_pdfs": len(pdfs),
            "processed": 0,
            "failed": 0,
            "files": []
        }
        
        for pdf_path in pdfs:
            try:
                info = self.get_pdf_info(pdf_path)
                
                # Copy PDF
                copied = self.copy_pdf(pdf_path)
                
                # Extract text if requested
                if extract_text:
                    text = self.extract_text_from_pdf(pdf_path)
                    if text:
                        self.save_extracted_text(pdf_path, text)
                
                results["processed"] += 1
                info["copied"] = str(copied) if copied else None
                results["files"].append(info)
                
            except Exception as e:
                self.logger.error(f"Error processing {pdf_path.name}: {e}")
                results["failed"] += 1
        
        return results


def main():
    """Example usage of PDFFileStore."""
    store = PDFFileStore()
    
    print("\n=== PDF File Store Manager ===\n")
    print(f"doc_dump directory: {store.doc_dump_path}")
    print(f"Extracted PDFs directory: {store.extracted_dir}\n")
    
    # List all PDFs
    pdfs = store.get_all_pdfs()
    if pdfs:
        print(f"Found {len(pdfs)} PDF(s):")
        for pdf in pdfs:
            info = store.get_pdf_info(pdf)
            print(f"  - {info['filename']} ({info['size_mb']}MB)")
        
        # Process all PDFs
        print("\nProcessing PDFs...")
        results = store.process_all_pdfs(extract_text=True)
        print(f"Processed: {results['processed']}/{results['total_pdfs']}")
        print(f"Failed: {results['failed']}")
    else:
        print("No PDFs found in doc_dump directory.")


if __name__ == "__main__":
    main()
