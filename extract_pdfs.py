#!/usr/bin/env python3
"""Find PDFs on local filesystem and extract them from doc_dump folder.

This script automatically searches the 'doc_dump' folder for PDF files and extracts them.

Usage examples:
  python3 extract_pdfs.py  # Searches doc_dump folder by default
  python3 extract_pdfs.py --extract-text  # Extract text from PDFs
  python3 extract_pdfs.py --output ./extracted_pdfs  # Custom output directory
  python3 extract_pdfs.py --dry-run  # Show what would be extracted
"""

from pathlib import Path
import argparse
import shutil
import logging
import sys


def parse_args():
    p = argparse.ArgumentParser(description="Find and extract PDF files from doc_dump")
    # Default to doc_dump folder
    script_dir = Path(__file__).parent
    default_doc_dump = str(script_dir / "doc_dump")
    p.add_argument("--start", "-s", nargs="+", default=[default_doc_dump], help="Start directory(ies) to search (default: ./doc_dump)")
    p.add_argument("--output", "-o", default="./extracted_pdfs", help="Output directory to extract PDFs into (default: ./extracted_pdfs)")
    p.add_argument("--move", action="store_true", help="Move files instead of copying (default: False)")
    p.add_argument("--pattern", "-p", default="**/*.pdf", help="Glob pattern to match PDF files (supports recursive patterns)")
    p.add_argument("--recursive", action="store_true", default=True, help="Search recursively (default: True)")
    p.add_argument("--no-recursive", dest="recursive", action="store_false", help="Do not search recursively")
    p.add_argument("--extract-text", action="store_true", help="Attempt to extract text from found PDFs (optional dependency: PyPDF2)")
    p.add_argument("--dry-run", action="store_true", help="Show actions without performing copy/move")
    p.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    return p.parse_args()


def find_pdfs(start: Path, pattern: str, recursive: bool):
    if recursive:
        return list(start.rglob(pattern.replace("**/", ""))) if pattern.startswith("**/") else list(start.rglob(pattern))
    else:
        return list(start.glob(pattern.replace("**/", "")))


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def try_import_pdf_reader():
    try:
        from PyPDF2 import PdfReader  # type: ignore
        return PdfReader
    except Exception:
        return None


def extract_text_from_pdf(reader_cls, src_path: Path, dest_txt: Path):
    try:
        reader = reader_cls(str(src_path)) if reader_cls.__name__ == "PdfReader" else reader_cls(str(src_path))
        text_parts = []
        for page in reader.pages:
            try:
                text_parts.append(page.extract_text() or "")
            except Exception:
                continue
        dest_txt.write_text("\n\n".join(text_parts), encoding="utf-8")
        logging.info("Extracted text to %s", dest_txt)
    except Exception as e:
        logging.warning("Failed extracting text from %s: %s", src_path, e)


def main():
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s: %(message)s")

    start_paths = [Path(s).expanduser() for s in args.start]
    output_base = Path(args.output).expanduser()
    ensure_dir(output_base)

    reader_cls = try_import_pdf_reader() if args.extract_text else None
    if args.extract_text and reader_cls is None:
        logging.warning("PyPDF2 not available; --extract-text will be skipped. Install with: pip install PyPDF2")

    found_any = False
    for start in start_paths:
        if not start.exists():
            logging.warning("Start path does not exist: %s", start)
            continue
        logging.info("Searching in %s", start)
        matches = find_pdfs(start, args.pattern, args.recursive)
        for src in matches:
            if not src.is_file():
                continue
            found_any = True
            # Create a destination path that preserves the relative path from the start directory
            try:
                rel = src.relative_to(start)
                dest = output_base / start.name / rel
            except Exception:
                # fallback: place under output with full name
                dest = output_base / src.name

            ensure_dir(dest.parent)
            action = "move" if args.move else "copy"
            if args.dry_run:
                logging.info("DRY RUN: %s %s -> %s", action.upper(), src, dest)
            else:
                if args.move:
                    shutil.move(str(src), str(dest))
                    logging.info("Moved %s -> %s", src, dest)
                else:
                    shutil.copy2(str(src), str(dest))
                    logging.info("Copied %s -> %s", src, dest)

                if reader_cls is not None:
                    dest_txt = dest.with_suffix(".txt")
                    extract_text_from_pdf(reader_cls, dest, dest_txt)

    if not found_any:
        logging.info("No PDF files found for the given start paths and pattern.")


if __name__ == "__main__":
    main()
