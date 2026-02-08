# AgenticRAG — PDF Extraction & Management

This utility finds PDF files in the `doc_dump` folder and automatically extracts them for processing. It can optionally extract text from PDFs (requires `PyPDF2`).

## Folder Structure

```
AgenticRAG/
├── doc_dump/                    # Upload PDFs here
│   ├── technical_guide.pdf
│   ├── quarterly_report.pdf
│   └── user_manual.pdf
├── extracted_pdfs/              # Extracted PDFs and text files
│   ├── technical_guide/
│   │   ├── technical_guide.pdf
│   │   └── technical_guide.txt
│   ├── quarterly_report/
│   │   ├── quarterly_report.pdf
│   │   └── quarterly_report.txt
│   └── user_manual/
│       ├── user_manual.pdf
│       └── user_manual.txt
├── extract_pdfs.py              # Script to extract PDFs
├── filestore.py                 # PDF storage management
└── requirements.txt
```

## Quick Start

### Method 1: Using filestore.py (Recommended)

Process all PDFs in `doc_dump` with text extraction:

```bash
python3 filestore.py
```

This will:
- Find all PDFs in `doc_dump/`
- Copy them to `extracted_pdfs/` (organized by filename)
- Extract text and save as `.txt` files

### Method 2: Using extract_pdfs.py

Extract PDFs from `doc_dump` (defaults to doc_dump folder):

```bash
python3 extract_pdfs.py
```

With text extraction:

```bash
python3 extract_pdfs.py --extract-text
```

Dry run (preview changes):

```bash
python3 extract_pdfs.py --dry-run
```

## Script Details

### filestore.py

Complete PDF management system with:
- Automatic `doc_dump` detection
- PDF discovery and metadata
- Text extraction from PDFs
- Organized file storage in `extracted_pdfs/`

```python
from filestore import PDFFileStore

store = PDFFileStore()  # Auto-detects doc_dump folder
pdfs = store.get_all_pdfs()
results = store.process_all_pdfs(extract_text=True)
```

### extract_pdfs.py

Flexible PDF extraction with options:
- `--start`: Search directory (defaults to `./doc_dump`)
- `--output`: Output directory (default: `./extracted_pdfs`)
- `--extract-text`: Extract text from PDFs
- `--move`: Move instead of copy
- `--dry-run`: Preview changes
- `--verbose`: Detailed logging

## How to Use

1. **Upload PDFs**: Place PDF files in the `doc_dump/` folder
2. **Run Extraction**: Execute `python3 filestore.py` or `python3 extract_pdfs.py`
3. **Access Results**: Find extracted files in `extracted_pdfs/`

## Dependencies

Optional (for text extraction):

```bash
pip install PyPDF2
```

## Installation

```bash
pip install -r requirements.txt
```
