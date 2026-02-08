#!/usr/bin/env python3
"""
Pipeline Test & Demonstration Script

This script tests the document parsing pipeline with sample PDFs.
"""

from pathlib import Path
from document_pipeline import DocumentPipeline, PipelineConfig
from pipeline_api import PipelineAPI
import time


def test_pipeline_basic():
    """Test basic pipeline functionality."""
    print("\n" + "="*70)
    print("TEST 1: Basic Pipeline Functionality")
    print("="*70)
    
    config = PipelineConfig(
        input_dir=Path("/Users/Shared/AgenticRAG/doc_dump"),
        output_dir=Path("/Users/Shared/AgenticRAG/doc_dump_md"),
        max_workers=2,
        cleanup_temp=True,
        log_level="INFO",
        use_threading=True
    )
    
    pipeline = DocumentPipeline(config)
    
    try:
        print("\nProcessing PDFs from doc_dump...")
        start_time = time.time()
        
        results = pipeline.process_batch()
        
        elapsed = time.time() - start_time
        successful = sum(1 for v in results.values() if v is not None)
        
        print("\n" + "-"*70)
        print("RESULTS:")
        print("-"*70)
        print(f"Total PDFs: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {len(results) - successful}")
        print(f"Time elapsed: {elapsed:.2f}s")
        
        if successful > 0:
            print("\nGenerated files:")
            for pdf_path, md_path in results.items():
                if md_path:
                    size_kb = md_path.stat().st_size / 1024
                    print(f"  ✓ {pdf_path.name}")
                    print(f"    → {md_path.name} ({size_kb:.1f}KB)")
        
        return successful > 0
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    finally:
        pipeline.cleanup()


def test_pipeline_api():
    """Test high-level API."""
    print("\n" + "="*70)
    print("TEST 2: High-Level API")
    print("="*70)
    
    api = PipelineAPI(
        max_workers=2,
        use_threading=True,
        verbose=False
    )
    
    try:
        print("\nUsing high-level API...")
        start_time = time.time()
        
        results = api.process_all_pdfs()
        
        elapsed = time.time() - start_time
        successful = sum(1 for v in results.values() if v is not None)
        
        print(f"\n✓ Processed {successful}/{len(results)} PDFs in {elapsed:.2f}s")
        
        # Get summary
        summary = api.get_processing_summary()
        print("\nProcessing Summary:")
        print(f"  Total files: {summary['total_files']}")
        print(f"  Total size: {summary['total_size_mb']}MB")
        
        return successful > 0
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_output_verification():
    """Verify output files were created."""
    print("\n" + "="*70)
    print("TEST 3: Output Verification")
    print("="*70)
    
    output_dir = Path("/Users/Shared/AgenticRAG/doc_dump_md")
    
    md_files = list(output_dir.glob("*.md"))
    
    print(f"\nGenerated markdown files: {len(md_files)}")
    
    if md_files:
        print("\nFile details:")
        total_size = 0
        for md_file in sorted(md_files):
            size = md_file.stat().st_size
            size_kb = size / 1024
            total_size += size
            
            # Count pages in markdown
            content = md_file.read_text()
            page_count = content.count("\n## Page ")
            
            print(f"  {md_file.name}")
            print(f"    Size: {size_kb:.1f}KB")
            print(f"    Pages: {page_count}")
        
        print(f"\nTotal size: {total_size / (1024*1024):.2f}MB")
        
        return len(md_files) > 0
    
    return False


def main():
    """Run all tests."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║              DOCUMENT PARSING PIPELINE - TEST SUITE                       ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    results = {
        "Basic Pipeline": test_pipeline_basic(),
        "High-Level API": test_pipeline_api(),
        "Output Verification": test_output_verification(),
    }
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("="*70)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
