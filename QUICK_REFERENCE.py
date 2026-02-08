#!/usr/bin/env python3
"""
DOCUMENT PARSING PIPELINE - QUICK REFERENCE GUIDE

Fast lookup for commands, APIs, and common tasks.
"""

QUICK_REFERENCE = """
╔════════════════════════════════════════════════════════════════════════════╗
║              DOCUMENT PARSING PIPELINE - QUICK REFERENCE                  ║
╚════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 MOST COMMON COMMANDS

# Process all PDFs in doc_dump/
$ python3 document_pipeline.py

# Use high-level API
$ python3 pipeline_api.py

# Run tests
$ python3 test_pipeline.py

# View guide
$ python3 PIPELINE_GUIDE.py

# View implementation summary
$ python3 IMPLEMENTATION_SUMMARY.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 PYTHON API - ONE-LINERS

# Process all PDFs
from pipeline_api import process_pdfs_simple
results = process_pdfs_simple()

# Process single PDF
from pipeline_api import process_single_pdf
result = process_single_pdf(Path("document.pdf"))

# Get summary statistics
from pipeline_api import get_summary
summary = get_summary()

# High-level API
from pipeline_api import PipelineAPI
api = PipelineAPI()
api.process_all_pdfs()

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 CONFIGURATION PRESETS

# Default (balanced): 4 workers
from pipeline_config import get_default_config
config = get_default_config()

# Fast: 8 workers
from pipeline_config import get_fast_config
config = get_fast_config()

# Debug: 1 worker, detailed logs
from pipeline_config import get_debug_config
config = get_debug_config()

# Memory efficient: 2 workers
from pipeline_config import get_memory_efficient_config
config = get_memory_efficient_config()

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 CUSTOM CONFIGURATION

from document_pipeline import DocumentPipeline, PipelineConfig
from pathlib import Path

config = PipelineConfig(
    input_dir=Path("./doc_dump"),
    output_dir=Path("./doc_dump_md"),
    max_workers=6,
    use_threading=True,
    log_level="INFO"
)

pipeline = DocumentPipeline(config)
results = pipeline.process_batch()

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 DIRECTORY STRUCTURE

Input:  /Users/Shared/AgenticRAG/doc_dump/
Output: /Users/Shared/AgenticRAG/doc_dump_md/

Example output files:
  - technical_guide.md
  - quarterly_report.md
  - user_manual.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ PERFORMANCE TUNING

Fast processing (more workers):
  max_workers=8, use_threading=True

Memory efficient (fewer workers):
  max_workers=2, use_threading=True

Debug/troubleshooting:
  max_workers=1, log_level="DEBUG"

Single large PDF:
  max_workers=1, use_threading=False

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 CORE CLASSES

PDFSplitter
  └─ split_pdf(pdf_path, output_dir) → List[Path]

DocumentParser
  └─ parse_document(doc_path) → Dict

MarkdownConverter
  └─ convert_to_markdown(parsed_content) → str

DocumentPipeline
  └─ process_pdf(pdf_path) → Optional[Path]
  └─ process_batch(pdf_files) → Dict[Path, Optional[Path]]

PipelineAPI
  └─ process_all_pdfs() → Dict
  └─ process_pdf(path) → Optional[Path]
  └─ get_processing_summary() → Dict

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🐛 TROUBLESHOOTING

ImportError: No module named 'fitz'
  → pip install pymupdf

ImportError: No module named 'docling'
  → pip install docling

PDF not processing
  → Check log_level="DEBUG" for error details
  → Verify PDF is valid and readable

Slow processing
  → Increase max_workers
  → Use use_threading=True

Memory issues
  → Reduce max_workers
  → Use memory_efficient_config

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 OUTPUT FORMAT

Each markdown file includes:
  • Document title
  • Generated from filename
  • Total pages count
  • Extracted content per page
  • Page markers for navigation
  • Processing summary with statistics

Example structure:
  # technical_guide
  **Generated from PDF**: technical_guide.pdf
  **Total Pages**: 1
  
  ---
  
  ## Page 1
  [extracted content]
  
  ---
  **Processing Summary**
  - Pages processed: 1
  - Successful extractions: 1
  - Failed extractions: 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 PRO TIPS

1. Process large PDF batches in multiple runs to manage memory
2. Use threading (default) for better performance with I/O
3. Monitor progress with log_level="INFO"
4. Save configurations to JSON for reproducibility
5. Clean output directory before new processing runs
6. Test with debug_config first on problematic PDFs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 FILE MANIFEST

Core Implementation:
  ✓ document_pipeline.py (17K)     Main pipeline implementation
  ✓ pipeline_config.py (10K)       Configuration management
  ✓ pipeline_api.py (11K)          High-level API

Documentation:
  ✓ PIPELINE_GUIDE.py (13K)        Comprehensive guide
  ✓ IMPLEMENTATION_SUMMARY.py (15K) Implementation overview
  ✓ QUICK_REFERENCE.py             This file

Testing:
  ✓ test_pipeline.py (5K)          Test suite

Input/Output:
  ✓ doc_dump/                      Input PDFs
  ✓ doc_dump_md/                   Output markdown files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔗 WORKFLOW SUMMARY

1. Place PDFs in doc_dump/
2. Run: python3 document_pipeline.py
3. Check output in doc_dump_md/
4. Access markdown files with extracted content

Or use Python API:
1. from pipeline_api import PipelineAPI
2. api = PipelineAPI()
3. api.process_all_pdfs()
4. results = api.get_processing_summary()

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Ready to process PDFs! ✨

For detailed help:
  • python3 PIPELINE_GUIDE.py - Full guide
  • python3 IMPLEMENTATION_SUMMARY.py - Implementation details
  • python3 pipeline_api.py - Interactive menu
  • python3 test_pipeline.py - Test examples

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

if __name__ == "__main__":
    print(QUICK_REFERENCE)
