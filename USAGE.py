#!/usr/bin/env python3
"""
Quick reference: How to use AgenticRAG PDF extraction tools
"""

def print_usage_guide():
    guide = """
╔════════════════════════════════════════════════════════════════════════════╗
║                    AgenticRAG PDF Extraction Guide                         ║
╚════════════════════════════════════════════════════════════════════════════╝

🗂️  FOLDER STRUCTURE:
    doc_dump/           ← Upload your PDFs here
    extracted_pdfs/     ← Extracted files will appear here automatically

📋 WORKFLOW:
    1. Place PDF files in doc_dump/ folder
    2. Run extraction script
    3. Access extracted PDFs and text in extracted_pdfs/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 QUICK START (Recommended):

   python3 filestore.py
   
   ✓ Finds all PDFs in doc_dump/
   ✓ Copies them to extracted_pdfs/ (organized by name)
   ✓ Extracts text automatically
   ✓ Saves text as .txt files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚙️  ALTERNATIVE: Using extract_pdfs.py

   Basic extraction (defaults to doc_dump):
   $ python3 extract_pdfs.py

   Extract with text:
   $ python3 extract_pdfs.py --extract-text

   Preview changes without executing:
   $ python3 extract_pdfs.py --dry-run

   Custom output directory:
   $ python3 extract_pdfs.py --output ./my_pdfs

   Verbose output:
   $ python3 extract_pdfs.py --verbose

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🐍 PYTHON API USAGE:

   from filestore import PDFFileStore
   
   # Initialize
   store = PDFFileStore()
   
   # Get all PDFs
   pdfs = store.get_all_pdfs()
   print(f"Found {len(pdfs)} PDFs")
   
   # Process all PDFs with text extraction
   results = store.process_all_pdfs(extract_text=True)
   print(f"Processed: {results['processed']}")
   
   # Extract text from specific PDF
   text = store.extract_text_from_pdf(pdfs[0])
   
   # Get PDF metadata
   info = store.get_pdf_info(pdfs[0])
   print(f"Size: {info['size_mb']}MB")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 DEPENDENCIES:

   Required:
   - Python 3.7+

   Optional (for text extraction):
   $ pip install PyPDF2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 OUTPUT STRUCTURE:

   extracted_pdfs/
   ├── technical_guide/
   │   ├── technical_guide.pdf        (original PDF)
   │   └── technical_guide.txt        (extracted text)
   ├── quarterly_report/
   │   ├── quarterly_report.pdf
   │   └── quarterly_report.txt
   └── user_manual/
       ├── user_manual.pdf
       └── user_manual.txt

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 TIPS:

   • Extracted text files contain page markers (--- Page X ---)
   • PDFs are organized in subdirectories by their filename
   • Text extraction requires PyPDF2 library
   • Use --dry-run to preview without making changes
   • Check logs for any extraction errors

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    print(guide)

if __name__ == "__main__":
    print_usage_guide()
