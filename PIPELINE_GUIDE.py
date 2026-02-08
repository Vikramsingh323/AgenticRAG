#!/usr/bin/env python3
"""
DOCUMENT PARSING PIPELINE - COMPREHENSIVE GUIDE

This guide covers the complete workflow for processing PDFs with:
- Page splitting (PyMuPDF)
- Document parsing (Docling)
- Markdown conversion
- Parallel processing
- Error handling
"""

GUIDE = """
╔════════════════════════════════════════════════════════════════════════════╗
║              DOCUMENT PARSING PIPELINE - COMPLETE GUIDE                   ║
╚════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 TABLE OF CONTENTS

1. Overview & Features
2. Architecture & Components
3. Installation & Setup
4. Quick Start Guide
5. Configuration Options
6. Usage Examples
7. API Reference
8. Troubleshooting
9. Performance Optimization

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. OVERVIEW & FEATURES

✓ PDF Page Division
  - Split PDFs into individual pages using PyMuPDF (fitz)
  - Sequential page naming for easy identification
  - Handles large documents efficiently

✓ Document Parsing
  - Parse pages using Docling library
  - Extract structured content (text, tables, images metadata)
  - Handles various PDF formats and layouts

✓ Markdown Conversion
  - Convert parsed content to well-formatted Markdown
  - Preserve document structure (headings, lists, tables)
  - Add page markers for easy navigation

✓ Parallel Processing
  - Process multiple pages concurrently
  - Configurable number of workers
  - Support for both threading and multiprocessing

✓ Error Handling
  - Graceful error recovery
  - Skip problematic pages and continue
  - Comprehensive logging and error reporting

✓ Flexible Configuration
  - Customizable processing parameters
  - Multiple preset configurations (default, fast, debug, memory-efficient)
  - Configuration file support (JSON)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. ARCHITECTURE & COMPONENTS

PipelineConfig
  └─ Dataclass holding configuration parameters
  └─ max_workers, batch_size, cleanup_temp, log_level, etc.

PipelineLogger
  └─ Custom logging with formatted output
  └─ info(), warning(), error(), debug() methods

PDFSplitter
  └─ Splits PDFs into individual pages
  └─ Uses PyMuPDF (fitz) for efficient handling
  └─ Returns list of page PDF paths

DocumentParser
  └─ Parses documents using Docling
  └─ Converts pages to structured format
  └─ Returns ConvertedDocument objects

MarkdownConverter
  └─ Converts parsed documents to Markdown
  └─ Preserves formatting and structure
  └─ Handles special content types

ParallelProcessor
  └─ Orchestrates parallel processing
  └─ Uses ThreadPoolExecutor or ProcessPoolExecutor
  └─ Manages worker allocation and error handling

DocumentPipeline
  └─ Main orchestration engine
  └─ Coordinates all components
  └─ Manages workflow and temporary files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. INSTALLATION & SETUP

Required packages:
  • pymupdf (fitz) - PDF page division
  • docling - Document parsing
  • python-docx - Optional, for advanced features

Installation:
  $ pip install pymupdf docling python-docx

Virtual environment (recommended):
  $ python3 -m venv venv
  $ source venv/bin/activate
  $ pip install -r requirements.txt

Verify installation:
  $ python3 -c "import fitz; import docling; print('✓ Ready')"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. QUICK START GUIDE

STEP 1: Prepare your PDFs
  └─ Place PDF files in: /Users/Shared/AgenticRAG/doc_dump/

STEP 2: Run the pipeline
  $ python3 document_pipeline.py

STEP 3: Access results
  └─ Check: /Users/Shared/AgenticRAG/doc_dump_md/
  └─ Find: filename.md files with extracted content

STEP 4: Review output
  └─ Open markdown files in text editor
  └─ Check quality and completeness
  └─ Adjust configuration if needed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. CONFIGURATION OPTIONS

Basic Configuration:
  
  config = PipelineConfig(
      input_dir=Path("./doc_dump"),
      output_dir=Path("./doc_dump_md"),
      max_workers=4,              # Number of parallel workers
      batch_size=10,              # Not currently used
      cleanup_temp=True,          # Clean up temp files after processing
      log_level="INFO",           # Logging level: DEBUG, INFO, WARNING, ERROR
      use_threading=True          # Use threading (True) or multiprocessing (False)
  )

Preset Configurations:

  1. Default (Balanced)
     max_workers=4, log_level="INFO", use_threading=True
  
  2. Fast (High Speed)
     max_workers=8, log_level="INFO", use_threading=True
  
  3. Debug (Detailed Logging)
     max_workers=1, log_level="DEBUG", use_threading=True
  
  4. Memory Efficient
     max_workers=2, log_level="INFO", use_threading=True

Configuration via JSON:

  {
    "input_dir": "/path/to/pdfs",
    "output_dir": "/path/to/output",
    "max_workers": 4,
    "use_threading": true,
    "log_level": "INFO",
    "cleanup_temp": true
  }

Load from file:
  config = AdvancedPipelineConfig.from_json_file(Path("config.json"))

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

6. USAGE EXAMPLES

EXAMPLE 1: Basic Usage (Command Line)

  $ python3 document_pipeline.py
  
  This will:
  - Find all PDFs in doc_dump/
  - Process them with default configuration
  - Save markdown to doc_dump_md/
  - Clean up temporary files


EXAMPLE 2: Process Specific PDFs (Python API)

  from pathlib import Path
  from document_pipeline import DocumentPipeline, PipelineConfig
  
  config = PipelineConfig(
      input_dir=Path("./doc_dump"),
      output_dir=Path("./doc_dump_md"),
      max_workers=4
  )
  
  pipeline = DocumentPipeline(config)
  
  pdf_files = [
      Path("./doc_dump/document1.pdf"),
      Path("./doc_dump/document2.pdf")
  ]
  
  results = pipeline.process_batch(pdf_files)
  
  for pdf_path, md_path in results.items():
      if md_path:
          print(f"✓ {pdf_path.name} → {md_path.name}")
      else:
          print(f"✗ {pdf_path.name} failed")


EXAMPLE 3: High-Level API

  from pipeline_api import PipelineAPI
  
  # Create API instance
  api = PipelineAPI(
      max_workers=8,
      use_threading=True,
      verbose=True
  )
  
  # Process all PDFs
  results = api.process_all_pdfs()
  
  # Get summary
  summary = api.get_processing_summary()
  print(f"Total files: {summary['total_files']}")
  print(f"Total size: {summary['total_size_mb']}MB")


EXAMPLE 4: Fast Processing

  from pipeline_config import get_fast_config
  from document_pipeline import DocumentPipeline
  
  config = get_fast_config()  # 8 workers
  pipeline = DocumentPipeline(config)
  results = pipeline.process_batch()
  pipeline.cleanup()


EXAMPLE 5: Debug Mode

  from pipeline_config import get_debug_config
  from document_pipeline import DocumentPipeline
  from pathlib import Path
  
  config = get_debug_config()  # Single worker, detailed logging
  pipeline = DocumentPipeline(config)
  
  # Process one PDF with detailed output
  pipeline.process_pdf(Path("./doc_dump/sample.pdf"))
  pipeline.cleanup()


EXAMPLE 6: Save Configuration

  from pipeline_config import AdvancedPipelineConfig
  from pathlib import Path
  
  config = AdvancedPipelineConfig(
      input_dir=Path("./doc_dump"),
      output_dir=Path("./doc_dump_md"),
      max_workers=4,
      log_level="INFO"
  )
  
  # Save to JSON
  config.to_json_file(Path("pipeline_config.json"))
  
  # Load later
  loaded = AdvancedPipelineConfig.from_json_file(Path("pipeline_config.json"))

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

7. API REFERENCE

DocumentPipeline class:

  __init__(config: PipelineConfig)
    └─ Initialize pipeline with configuration

  process_pdf(pdf_path: Path) -> Optional[Path]
    └─ Process single PDF
    └─ Returns: Path to output markdown or None

  process_batch(pdf_files: Optional[List[Path]]) -> Dict[Path, Optional[Path]]
    └─ Process multiple PDFs
    └─ Returns: Dictionary mapping input PDFs to output markdowns

  cleanup()
    └─ Clean up temporary files

PipelineAPI class (High-level interface):

  __init__(input_dir, output_dir, max_workers, use_threading, verbose)
    └─ Initialize API

  process_all_pdfs() -> Dict[Path, Optional[Path]]
    └─ Process all PDFs in input directory

  process_pdf(pdf_path: Path) -> Optional[Path]
    └─ Process single PDF

  process_pdfs(pdf_files: List[Path]) -> Dict[Path, Optional[Path]]
    └─ Process specific PDFs

  get_output_files() -> List[Path]
    └─ Get all generated markdown files

  get_processing_summary() -> Dict
    └─ Get summary statistics

  clear_output(confirm: bool) -> bool
    └─ Clear output files

Convenience functions:

  process_pdfs_simple(input_dir, output_dir, max_workers)
    └─ Quick processing of all PDFs

  process_single_pdf(pdf_path, output_dir, max_workers)
    └─ Quick processing of single PDF

  get_summary(output_dir)
    └─ Get processing summary

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

8. TROUBLESHOOTING

Issue: "ModuleNotFoundError: No module named 'fitz'"
Solution: pip install pymupdf

Issue: "ModuleNotFoundError: No module named 'docling'"
Solution: pip install docling

Issue: PDF not processing
Check:
  - File exists and is valid
  - File is readable
  - Sufficient disk space for temp files
  - Check logs for specific error messages

Issue: Slow processing
Solutions:
  - Increase max_workers (up to CPU count)
  - Use threading instead of multiprocessing
  - Process PDFs in batches

Issue: Memory issues
Solutions:
  - Reduce max_workers
  - Process fewer PDFs at once
  - Use memory_efficient_config

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

9. PERFORMANCE OPTIMIZATION

Tuning max_workers:
  - Start: match CPU core count
  - Threading: can go higher (I/O bound)
  - Multiprocessing: keep at CPU count or lower

Memory optimization:
  - Reduce max_workers
  - Process in smaller batches
  - Enable cleanup_temp

Speed optimization:
  - Increase max_workers
  - Use threading (less overhead)
  - Pre-warm the converter

Benchmarks (Example):
  - Default (4 workers): ~2.5 min for 10 PDFs
  - Fast (8 workers): ~1.5 min for 10 PDFs
  - Debug (1 worker): ~10 min for 10 PDFs (with logging)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 ADDITIONAL RESOURCES

Files:
  - document_pipeline.py: Core pipeline implementation
  - pipeline_config.py: Configuration utilities and examples
  - pipeline_api.py: High-level API for programmatic use
  - PIPELINE_GUIDE.py: This guide

Directories:
  - doc_dump/: Input PDF directory
  - doc_dump_md/: Output markdown directory
  - .temp_*: Temporary directories (auto-cleaned)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

if __name__ == "__main__":
    print(GUIDE)
