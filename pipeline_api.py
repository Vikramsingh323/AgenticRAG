#!/usr/bin/env python3
"""
Document Pipeline API - High-level interface for document processing.

This module provides a simplified API for processing documents programmatically.

Example:
    from pipeline_api import PipelineAPI
    
    api = PipelineAPI()
    results = api.process_all_pdfs()
    
    for pdf_path, md_path in results.items():
        if md_path:
            print(f"✓ {pdf_path.name} → {md_path.name}")
"""

from pathlib import Path
from typing import Optional, List, Dict, Callable
from document_pipeline import DocumentPipeline, PipelineConfig, PipelineLogger
import time


class PipelineAPI:
    """High-level API for document processing."""
    
    def __init__(
        self,
        input_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        max_workers: int = 4,
        use_threading: bool = True,
        verbose: bool = False
    ):
        """
        Initialize the pipeline API.
        
        Args:
            input_dir: Directory containing PDFs (default: doc_dump)
            output_dir: Directory for markdown output (default: doc_dump_md)
            max_workers: Number of parallel workers
            use_threading: Use threading instead of multiprocessing
            verbose: Enable verbose logging
        """
        self.input_dir = input_dir or Path("/Users/Shared/AgenticRAG/doc_dump")
        self.output_dir = output_dir or Path("/Users/Shared/AgenticRAG/doc_dump_md")
        self.max_workers = max_workers
        self.use_threading = use_threading
        self.verbose = verbose
        
        log_level = "DEBUG" if verbose else "INFO"
        
        self.config = PipelineConfig(
            input_dir=self.input_dir,
            output_dir=self.output_dir,
            max_workers=max_workers,
            cleanup_temp=True,
            log_level=log_level,
            use_threading=use_threading
        )
        
        self.pipeline = DocumentPipeline(self.config)
        self.logger = self.pipeline.logger
    
    def process_all_pdfs(self) -> Dict[Path, Optional[Path]]:
        """
        Process all PDFs in input directory.
        
        Returns:
            Dictionary mapping input PDFs to output markdown files
        """
        start_time = time.time()
        
        try:
            results = self.pipeline.process_batch()
            
            elapsed = time.time() - start_time
            successful = sum(1 for v in results.values() if v is not None)
            
            self.logger.info(f"\n✓ Processing completed in {elapsed:.2f}s")
            self.logger.info(f"  Successfully processed: {successful}/{len(results)}")
            
            return results
            
        finally:
            self.pipeline.cleanup()
    
    def process_pdf(self, pdf_path: Path) -> Optional[Path]:
        """
        Process a single PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Path to output markdown file or None if failed
        """
        start_time = time.time()
        
        try:
            result = self.pipeline.process_pdf(pdf_path)
            
            elapsed = time.time() - start_time
            status = "✓ Success" if result else "✗ Failed"
            self.logger.info(f"{status} ({elapsed:.2f}s)")
            
            return result
            
        finally:
            self.pipeline.cleanup()
    
    def process_pdfs(self, pdf_files: List[Path]) -> Dict[Path, Optional[Path]]:
        """
        Process multiple specific PDF files.
        
        Args:
            pdf_files: List of PDF file paths
            
        Returns:
            Dictionary mapping input PDFs to output markdown files
        """
        start_time = time.time()
        
        try:
            results = self.pipeline.process_batch(pdf_files)
            
            elapsed = time.time() - start_time
            successful = sum(1 for v in results.values() if v is not None)
            
            self.logger.info(f"\n✓ Batch processing completed in {elapsed:.2f}s")
            self.logger.info(f"  Successfully processed: {successful}/{len(results)}")
            
            return results
            
        finally:
            self.pipeline.cleanup()
    
    def get_output_files(self) -> List[Path]:
        """
        Get list of all generated markdown files.
        
        Returns:
            List of paths to markdown files
        """
        return sorted(self.output_dir.glob("*.md"))
    
    def get_processing_summary(self) -> Dict[str, any]:
        """
        Get summary of processing results.
        
        Returns:
            Dictionary with summary statistics
        """
        md_files = self.get_output_files()
        
        total_size = sum(f.stat().st_size for f in md_files)
        total_pages = sum(
            f.read_text().count("\n## Page ")
            for f in md_files
        )
        
        return {
            "total_files": len(md_files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "estimated_pages": total_pages,
            "output_directory": str(self.output_dir),
            "files": [
                {
                    "name": f.name,
                    "size_kb": round(f.stat().st_size / 1024, 2),
                    "path": str(f)
                }
                for f in md_files
            ]
        }
    
    def clear_output(self, confirm: bool = False) -> bool:
        """
        Clear all generated markdown files.
        
        Args:
            confirm: Require user confirmation
            
        Returns:
            True if cleared successfully
        """
        if not self.output_dir.exists():
            self.logger.warning("Output directory does not exist")
            return False
        
        md_files = self.get_output_files()
        
        if not md_files:
            self.logger.info("No markdown files to clear")
            return True
        
        if confirm:
            user_input = input(f"Clear {len(md_files)} markdown files? (y/n): ")
            if user_input.lower() != 'y':
                self.logger.info("Cancelled")
                return False
        
        try:
            for f in md_files:
                f.unlink()
            self.logger.info(f"✓ Cleared {len(md_files)} markdown files")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing files: {e}")
            return False


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def process_pdfs_simple(
    input_dir: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    max_workers: int = 4
) -> Dict[Path, Optional[Path]]:
    """
    Simple function to process all PDFs.
    
    Args:
        input_dir: Directory with PDFs
        output_dir: Directory for markdown output
        max_workers: Number of parallel workers
        
    Returns:
        Dictionary mapping input PDFs to output markdown files
        
    Example:
        results = process_pdfs_simple()
        for pdf, md in results.items():
            if md:
                print(f"✓ {pdf.name} → {md.name}")
    """
    api = PipelineAPI(input_dir, output_dir, max_workers, verbose=False)
    return api.process_all_pdfs()


def process_single_pdf(
    pdf_path: Path,
    output_dir: Optional[Path] = None,
    max_workers: int = 4
) -> Optional[Path]:
    """
    Process a single PDF file.
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Directory for markdown output
        max_workers: Number of parallel workers
        
    Returns:
        Path to output markdown file or None
        
    Example:
        md_path = process_single_pdf(Path("document.pdf"))
        if md_path:
            print(f"✓ Processed to {md_path}")
    """
    api = PipelineAPI(output_dir=output_dir, max_workers=max_workers, verbose=False)
    return api.process_pdf(pdf_path)


def get_summary(output_dir: Optional[Path] = None) -> Dict:
    """
    Get summary of processing results.
    
    Args:
        output_dir: Directory with markdown files
        
    Returns:
        Summary dictionary
        
    Example:
        summary = get_summary()
        print(f"Total files: {summary['total_files']}")
        print(f"Total size: {summary['total_size_mb']}MB")
    """
    api = PipelineAPI(output_dir=output_dir)
    return api.get_processing_summary()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Interactive pipeline API demonstration."""
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    PIPELINE API - INTERACTIVE DEMO                        ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    api = PipelineAPI(verbose=True)
    
    while True:
        print("\n" + "="*70)
        print("PIPELINE API MENU")
        print("="*70)
        print("1. Process all PDFs")
        print("2. Process single PDF")
        print("3. View processing summary")
        print("4. Clear output files")
        print("5. Exit")
        print("="*70)
        
        choice = input("Select option (1-5): ").strip()
        
        if choice == "1":
            print("\nProcessing all PDFs...")
            results = api.process_all_pdfs()
            successful = sum(1 for v in results.values() if v is not None)
            print(f"✓ {successful}/{len(results)} PDFs processed successfully")
            
        elif choice == "2":
            pdf_path = input("Enter PDF file path: ").strip()
            pdf_file = Path(pdf_path)
            if pdf_file.exists():
                print(f"\nProcessing {pdf_file.name}...")
                result = api.process_pdf(pdf_file)
                if result:
                    print(f"✓ Successfully processed to {result.name}")
                else:
                    print("✗ Processing failed")
            else:
                print(f"✗ File not found: {pdf_path}")
        
        elif choice == "3":
            summary = api.get_processing_summary()
            print("\n" + "="*70)
            print("PROCESSING SUMMARY")
            print("="*70)
            print(f"Total markdown files: {summary['total_files']}")
            print(f"Total size: {summary['total_size_mb']}MB")
            print(f"Estimated pages: {summary['estimated_pages']}")
            print(f"Output directory: {summary['output_directory']}")
            
            if summary['files']:
                print("\nFiles:")
                for file_info in summary['files']:
                    print(f"  - {file_info['name']} ({file_info['size_kb']}KB)")
        
        elif choice == "4":
            if api.clear_output(confirm=True):
                print("✓ Output files cleared")
        
        elif choice == "5":
            print("Exiting...")
            break
        
        else:
            print("✗ Invalid option")


if __name__ == "__main__":
    main()
