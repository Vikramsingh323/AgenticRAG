#!/usr/bin/env python3
"""
Document Parsing Pipeline - Processes PDFs with the following workflow:
1. PDF Page Division (PyMuPDF)
2. Document Parsing (Docling)
3. Markdown Conversion & Output
4. Error Handling & Logging
5. Configurable Processing

Author: AgenticRAG
Date: February 2026
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
import fitz  # PyMuPDF
from docling.document_converter import DocumentConverter
import json


# ============================================================================
# CONFIGURATION & LOGGING
# ============================================================================

@dataclass
class PipelineConfig:
    """Configuration for the document parsing pipeline."""
    input_dir: Path
    output_dir: Path
    temp_dir: Optional[Path] = None
    max_workers: int = 4
    batch_size: int = 10
    cleanup_temp: bool = True
    log_level: str = "INFO"
    use_threading: bool = False  # Use threading instead of multiprocessing


class PipelineLogger:
    """Custom logger for the pipeline."""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
    
    def info(self, msg: str):
        self.logger.info(msg)
    
    def warning(self, msg: str):
        self.logger.warning(msg)
    
    def error(self, msg: str):
        self.logger.error(msg)
    
    def debug(self, msg: str):
        self.logger.debug(msg)


# ============================================================================
# PDF PAGE DIVISION (PyMuPDF)
# ============================================================================

class PDFSplitter:
    """Splits PDF files into individual pages."""
    
    def __init__(self, logger: PipelineLogger):
        self.logger = logger
    
    def split_pdf(self, pdf_path: Path, output_dir: Path) -> List[Path]:
        """
        Split a PDF into individual page files.
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save split pages
            
        Returns:
            List of paths to split page PDFs
            
        Raises:
            Exception: If PDF cannot be read
        """
        try:
            self.logger.info(f"Splitting PDF: {pdf_path.name}")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Open PDF document
            doc = fitz.open(str(pdf_path))
            split_pages = []
            
            self.logger.info(f"  Total pages: {len(doc)}")
            
            # Extract each page
            for page_num in range(len(doc)):
                try:
                    # Create new PDF with single page
                    new_doc = fitz.open()
                    new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                    
                    # Generate output filename
                    stem = pdf_path.stem
                    page_filename = f"{stem}_page_{page_num + 1:03d}.pdf"
                    page_path = output_dir / page_filename
                    
                    # Save page
                    new_doc.save(str(page_path))
                    new_doc.close()
                    
                    split_pages.append(page_path)
                    
                except Exception as e:
                    self.logger.warning(f"  Error extracting page {page_num + 1}: {e}")
                    continue
            
            doc.close()
            
            self.logger.info(f"  Successfully split into {len(split_pages)} pages")
            return split_pages
            
        except Exception as e:
            self.logger.error(f"Failed to split PDF {pdf_path.name}: {e}")
            raise


# ============================================================================
# DOCUMENT PARSING (Docling)
# ============================================================================

class DocumentParser:
    """Parses documents using Docling library."""
    
    def __init__(self, logger: PipelineLogger):
        self.logger = logger
        self.converter = DocumentConverter()
    
    def parse_document(self, doc_path: Path) -> Optional[Dict[str, Any]]:
        """
        Parse a document using Docling.
        
        Args:
            doc_path: Path to the document (PDF or other format)
            
        Returns:
            Dictionary with parsed content or None if parsing fails
        """
        try:
            self.logger.debug(f"Parsing: {doc_path.name}")
            result = self.converter.convert(str(doc_path))
            
            # Convert result to dictionary for serialization
            if result:
                return {
                    'document': str(result.document),
                    'success': True
                }
            return None
            
        except Exception as e:
            self.logger.warning(f"Error parsing {doc_path.name}: {e}")
            return None


# ============================================================================
# MARKDOWN CONVERSION
# ============================================================================

class MarkdownConverter:
    """Converts parsed documents to Markdown format."""
    
    def __init__(self, logger: PipelineLogger):
        self.logger = logger
    
    def convert_to_markdown(self, parsed_content: Dict[str, Any]) -> str:
        """
        Convert parsed content to Markdown format.
        
        Args:
            parsed_content: Dictionary with parsed document content
            
        Returns:
            Markdown string
        """
        try:
            if not parsed_content or not parsed_content.get('document'):
                return ""
            
            # Convert the document content to markdown
            content = parsed_content.get('document', '')
            
            # Basic markdown formatting for text content
            markdown = self._format_as_markdown(content)
            return markdown
                
        except Exception as e:
            self.logger.warning(f"Error converting document to markdown: {e}")
            return ""
    
    def _format_as_markdown(self, text: str) -> str:
        """Format text as markdown."""
        # Simple formatting - add basic markdown structure
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                formatted_lines.append('')
            else:
                # Preserve paragraph structure
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)


# ============================================================================
# PARALLEL PROCESSING
# ============================================================================

class ParallelProcessor:
    """Handles parallel processing of documents."""
    
    def __init__(self, config: PipelineConfig, logger: PipelineLogger):
        self.config = config
        self.logger = logger
        self.parser = DocumentParser(logger)
    
    def process_page(self, page_path: Path) -> Tuple[Path, Optional[str]]:
        """
        Process a single page (for parallel execution).
        
        Args:
            page_path: Path to page PDF
            
        Returns:
            Tuple of (page_path, markdown_content or None)
        """
        converted = self.parser.parse_document(page_path)
        
        if converted is None:
            return page_path, None
        
        converter = MarkdownConverter(self.logger)
        markdown = converter.convert_to_markdown(converted)
        
        return page_path, markdown
    
    def process_pages_parallel(self, page_paths: List[Path]) -> Dict[Path, Optional[str]]:
        """
        Process multiple pages in parallel.
        
        Args:
            page_paths: List of page PDF paths
            
        Returns:
            Dictionary mapping page_path to markdown content
        """
        results = {}
        executor_class = ThreadPoolExecutor if self.config.use_threading else ProcessPoolExecutor
        
        self.logger.info(f"Processing {len(page_paths)} pages with {self.config.max_workers} workers...")
        
        with executor_class(max_workers=self.config.max_workers) as executor:
            futures = {
                executor.submit(self.process_page, page_path): page_path 
                for page_path in page_paths
            }
            
            completed = 0
            for future in as_completed(futures):
                try:
                    page_path, markdown = future.result()
                    results[page_path] = markdown
                    completed += 1
                    
                    if completed % max(1, len(page_paths) // 10) == 0 or completed == len(page_paths):
                        self.logger.info(f"  Processed: {completed}/{len(page_paths)}")
                        
                except Exception as e:
                    self.logger.error(f"Error processing page: {e}")
        
        return results


# ============================================================================
# DOCUMENT PIPELINE
# ============================================================================

class DocumentPipeline:
    """Main pipeline orchestrating the entire workflow."""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.logger = PipelineLogger("DocumentPipeline", config.log_level)
        self.splitter = PDFSplitter(self.logger)
        self.processor = ParallelProcessor(config, self.logger)
        self.markdown_converter = MarkdownConverter(self.logger)
        
        # Create temp directory
        if config.temp_dir is None:
            self.temp_dir = Path(tempfile.mkdtemp(prefix="doc_split_"))
        else:
            self.temp_dir = config.temp_dir
            self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Create output directory
        config.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Pipeline initialized")
        self.logger.info(f"  Temp dir: {self.temp_dir}")
        self.logger.info(f"  Output dir: {config.output_dir}")
        self.logger.info(f"  Max workers: {config.max_workers}")
    
    def process_pdf(self, pdf_path: Path) -> Optional[Path]:
        """
        Process a single PDF file through the entire pipeline.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Path to output markdown file or None if processing fails
        """
        try:
            self.logger.info(f"\n{'='*70}")
            self.logger.info(f"Processing PDF: {pdf_path.name}")
            self.logger.info(f"{'='*70}")
            
            if not pdf_path.exists():
                self.logger.error(f"PDF file not found: {pdf_path}")
                return None
            
            # Step 1: Split PDF into pages
            pdf_temp_dir = self.temp_dir / pdf_path.stem
            page_paths = self.splitter.split_pdf(pdf_path, pdf_temp_dir)
            
            if not page_paths:
                self.logger.error(f"No pages extracted from {pdf_path.name}")
                return None
            
            # Step 2: Process pages in parallel
            page_markdowns = self.processor.process_pages_parallel(page_paths)
            
            # Step 3: Combine markdowns
            combined_markdown = self._combine_markdowns(
                pdf_path.stem,
                page_markdowns,
                page_paths
            )
            
            # Step 4: Save output
            output_path = self.config.output_dir / f"{pdf_path.stem}.md"
            output_path.write_text(combined_markdown, encoding='utf-8')
            
            self.logger.info(f"✓ Saved markdown: {output_path.name}")
            self.logger.info(f"  File size: {output_path.stat().st_size} bytes")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to process PDF {pdf_path.name}: {e}")
            return None
    
    def _combine_markdowns(self, pdf_name: str, page_markdowns: Dict[Path, Optional[str]], 
                          page_paths: List[Path]) -> str:
        """
        Combine individual page markdowns into a single document.
        
        Args:
            pdf_name: Original PDF filename (without extension)
            page_markdowns: Dictionary mapping page paths to markdown content
            page_paths: List of page paths in order
            
        Returns:
            Combined markdown string
        """
        combined_parts = []
        
        # Add header
        combined_parts.append(f"# {pdf_name}\n")
        combined_parts.append(f"**Generated from PDF**: {pdf_name}.pdf\n")
        combined_parts.append(f"**Total Pages**: {len(page_paths)}\n\n")
        combined_parts.append("---\n\n")
        
        # Add page contents
        successful_pages = 0
        failed_pages = 0
        
        for i, page_path in enumerate(page_paths, 1):
            page_markdown = page_markdowns.get(page_path)
            
            if page_markdown:
                combined_parts.append(f"## Page {i}\n\n")
                combined_parts.append(page_markdown)
                combined_parts.append("\n\n---\n\n")
                successful_pages += 1
            else:
                combined_parts.append(f"## Page {i}\n\n")
                combined_parts.append("*(Failed to extract content from this page)*\n\n")
                combined_parts.append("---\n\n")
                failed_pages += 1
        
        # Add summary
        combined_parts.append("\n---\n")
        combined_parts.append(f"**Processing Summary**\n")
        combined_parts.append(f"- Pages processed: {len(page_paths)}\n")
        combined_parts.append(f"- Successful extractions: {successful_pages}\n")
        combined_parts.append(f"- Failed extractions: {failed_pages}\n")
        
        return "".join(combined_parts)
    
    def process_batch(self, pdf_files: Optional[List[Path]] = None) -> Dict[Path, Optional[Path]]:
        """
        Process a batch of PDF files.
        
        Args:
            pdf_files: List of PDF file paths. If None, finds all PDFs in input_dir
            
        Returns:
            Dictionary mapping input PDFs to output markdown files
        """
        # Find PDF files
        if pdf_files is None:
            pdf_files = list(self.config.input_dir.glob("*.pdf"))
        
        if not pdf_files:
            self.logger.warning("No PDF files found to process")
            return {}
        
        self.logger.info(f"Found {len(pdf_files)} PDF file(s) to process")
        
        results = {}
        for pdf_path in pdf_files:
            output_path = self.process_pdf(pdf_path)
            results[pdf_path] = output_path
        
        return results
    
    def cleanup(self):
        """Clean up temporary files."""
        if self.config.cleanup_temp and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                self.logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                self.logger.warning(f"Error cleaning up temp directory: {e}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Example usage of the document parsing pipeline."""
    
    # Configure pipeline
    config = PipelineConfig(
        input_dir=Path("/Users/Shared/AgenticRAG/doc_dump"),
        output_dir=Path("/Users/Shared/AgenticRAG/doc_dump_md"),
        max_workers=4,
        batch_size=10,
        cleanup_temp=True,
        log_level="INFO",
        use_threading=True  # Use threading for I/O bound operations
    )
    
    # Create and run pipeline
    pipeline = DocumentPipeline(config)
    
    try:
        # Process all PDFs in input directory
        results = pipeline.process_batch()
        
        # Print summary
        print("\n" + "="*70)
        print("PROCESSING COMPLETE")
        print("="*70)
        
        successful = sum(1 for v in results.values() if v is not None)
        total = len(results)
        
        print(f"Total PDFs processed: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        
        if successful > 0:
            print(f"\nOutput directory: {config.output_dir}")
            print("\nGenerated markdown files:")
            for md_file in sorted(config.output_dir.glob("*.md")):
                size_kb = md_file.stat().st_size / 1024
                print(f"  - {md_file.name} ({size_kb:.1f}KB)")
        
    finally:
        # Cleanup temp files
        pipeline.cleanup()


if __name__ == "__main__":
    main()
