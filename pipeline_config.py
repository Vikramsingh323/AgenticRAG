#!/usr/bin/env python3
"""
Pipeline Configuration & Usage Examples

This module provides configuration utilities and examples for the document parsing pipeline.
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List
import json
from document_pipeline import PipelineConfig, DocumentPipeline


@dataclass
class AdvancedPipelineConfig:
    """Advanced configuration with additional settings."""
    
    # Core settings
    input_dir: Path
    output_dir: Path
    
    # Processing options
    max_workers: int = 4
    batch_size: int = 10
    use_threading: bool = True
    
    # Storage options
    temp_dir: Optional[Path] = None
    cleanup_temp: bool = True
    keep_split_pages: bool = False
    
    # Logging options
    log_level: str = "INFO"
    save_processing_log: bool = True
    log_file: Optional[Path] = None
    
    # Format options
    include_page_numbers: bool = True
    include_metadata: bool = True
    markdown_style: str = "standard"  # standard, compact, detailed
    
    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "input_dir": str(self.input_dir),
            "output_dir": str(self.output_dir),
            "max_workers": self.max_workers,
            "batch_size": self.batch_size,
            "use_threading": self.use_threading,
            "temp_dir": str(self.temp_dir) if self.temp_dir else None,
            "cleanup_temp": self.cleanup_temp,
            "keep_split_pages": self.keep_split_pages,
            "log_level": self.log_level,
            "save_processing_log": self.save_processing_log,
            "include_page_numbers": self.include_page_numbers,
            "include_metadata": self.include_metadata,
            "markdown_style": self.markdown_style,
        }
    
    def to_json_file(self, filepath: Path):
        """Save configuration to JSON file."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def from_json_file(cls, filepath: Path) -> 'AdvancedPipelineConfig':
        """Load configuration from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Convert string paths back to Path objects
        if data['temp_dir']:
            data['temp_dir'] = Path(data['temp_dir'])
        
        data['input_dir'] = Path(data['input_dir'])
        data['output_dir'] = Path(data['output_dir'])
        
        return cls(**data)


# ============================================================================
# EXAMPLE CONFIGURATIONS
# ============================================================================

def get_default_config() -> PipelineConfig:
    """Get default configuration."""
    return PipelineConfig(
        input_dir=Path("/Users/Shared/AgenticRAG/doc_dump"),
        output_dir=Path("/Users/Shared/AgenticRAG/doc_dump_md"),
        max_workers=4,
        batch_size=10,
        cleanup_temp=True,
        log_level="INFO",
        use_threading=True
    )


def get_fast_config() -> PipelineConfig:
    """Configuration optimized for speed (more workers)."""
    return PipelineConfig(
        input_dir=Path("/Users/Shared/AgenticRAG/doc_dump"),
        output_dir=Path("/Users/Shared/AgenticRAG/doc_dump_md"),
        max_workers=8,  # More workers
        batch_size=20,
        cleanup_temp=True,
        log_level="INFO",
        use_threading=True
    )


def get_debug_config() -> PipelineConfig:
    """Configuration for debugging (detailed logging, single worker)."""
    return PipelineConfig(
        input_dir=Path("/Users/Shared/AgenticRAG/doc_dump"),
        output_dir=Path("/Users/Shared/AgenticRAG/doc_dump_md"),
        max_workers=1,  # Single worker for debugging
        batch_size=1,
        cleanup_temp=False,
        log_level="DEBUG",
        use_threading=True
    )


def get_memory_efficient_config() -> PipelineConfig:
    """Configuration for limited memory environments."""
    return PipelineConfig(
        input_dir=Path("/Users/Shared/AgenticRAG/doc_dump"),
        output_dir=Path("/Users/Shared/AgenticRAG/doc_dump_md"),
        max_workers=2,  # Fewer workers
        batch_size=5,
        cleanup_temp=True,
        log_level="INFO",
        use_threading=True
    )


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

def example_basic_usage():
    """Example 1: Basic usage with default configuration."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Usage")
    print("="*70)
    
    config = get_default_config()
    pipeline = DocumentPipeline(config)
    
    try:
        results = pipeline.process_batch()
        print(f"\nProcessed {len(results)} PDFs successfully!")
    finally:
        pipeline.cleanup()


def example_custom_input():
    """Example 2: Process specific PDF files."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Process Specific PDFs")
    print("="*70)
    
    config = get_default_config()
    pipeline = DocumentPipeline(config)
    
    try:
        # Process only specific PDFs
        pdf_files = [
            Path("/Users/Shared/AgenticRAG/doc_dump/technical_guide.pdf"),
            Path("/Users/Shared/AgenticRAG/doc_dump/quarterly_report.pdf"),
        ]
        
        results = pipeline.process_batch(pdf_files)
        
        print("\nResults:")
        for pdf_path, md_path in results.items():
            status = "✓ Success" if md_path else "✗ Failed"
            print(f"  {pdf_path.name}: {status}")
    
    finally:
        pipeline.cleanup()


def example_fast_processing():
    """Example 3: Fast processing with more workers."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Fast Processing (8 workers)")
    print("="*70)
    
    config = get_fast_config()
    pipeline = DocumentPipeline(config)
    
    try:
        results = pipeline.process_batch()
        successful = sum(1 for v in results.values() if v is not None)
        print(f"\nProcessed {len(results)} PDFs with {successful} successful!")
    finally:
        pipeline.cleanup()


def example_debug_mode():
    """Example 4: Debug mode with detailed logging."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Debug Mode (Single Worker, Detailed Logging)")
    print("="*70)
    
    config = get_debug_config()
    pipeline = DocumentPipeline(config)
    
    try:
        # Process just one PDF for debugging
        pdf_file = Path("/Users/Shared/AgenticRAG/doc_dump/technical_guide.pdf")
        if pdf_file.exists():
            pipeline.process_pdf(pdf_file)
        else:
            print(f"PDF not found: {pdf_file}")
    finally:
        pipeline.cleanup()


def example_custom_config():
    """Example 5: Custom configuration."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Custom Configuration")
    print("="*70)
    
    config = PipelineConfig(
        input_dir=Path("/Users/Shared/AgenticRAG/doc_dump"),
        output_dir=Path("/Users/Shared/AgenticRAG/doc_dump_md"),
        max_workers=6,
        batch_size=15,
        cleanup_temp=True,
        log_level="INFO",
        use_threading=True
    )
    
    pipeline = DocumentPipeline(config)
    
    try:
        results = pipeline.process_batch()
        
        # Print summary
        successful = sum(1 for v in results.values() if v is not None)
        print(f"\n✓ Processed {successful}/{len(results)} PDFs successfully")
        
    finally:
        pipeline.cleanup()


def example_save_config():
    """Example 6: Save and load configuration."""
    print("\n" + "="*70)
    print("EXAMPLE 6: Save and Load Configuration")
    print("="*70)
    
    # Create config
    config = AdvancedPipelineConfig(
        input_dir=Path("/Users/Shared/AgenticRAG/doc_dump"),
        output_dir=Path("/Users/Shared/AgenticRAG/doc_dump_md"),
        max_workers=4,
        use_threading=True,
        log_level="INFO"
    )
    
    # Save to file
    config_file = Path("/Users/Shared/AgenticRAG/pipeline_config.json")
    config.to_json_file(config_file)
    print(f"✓ Configuration saved to: {config_file}")
    
    # Load from file
    loaded_config = AdvancedPipelineConfig.from_json_file(config_file)
    print(f"✓ Configuration loaded from: {config_file}")
    print(f"  Input dir: {loaded_config.input_dir}")
    print(f"  Max workers: {loaded_config.max_workers}")


if __name__ == "__main__":
    import sys
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                  DOCUMENT PARSING PIPELINE - EXAMPLES                      ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Run all examples or specific one
    if len(sys.argv) > 1:
        example_num = int(sys.argv[1])
        examples = {
            1: example_basic_usage,
            2: example_custom_input,
            3: example_fast_processing,
            4: example_debug_mode,
            5: example_custom_config,
            6: example_save_config,
        }
        
        if example_num in examples:
            examples[example_num]()
        else:
            print(f"Example {example_num} not found. Available: 1-6")
    else:
        # Run basic example
        example_basic_usage()
        print("\n" + "="*70)
        print("To run other examples:")
        print("  python3 pipeline_config.py 1  # Basic usage")
        print("  python3 pipeline_config.py 2  # Custom input")
        print("  python3 pipeline_config.py 3  # Fast processing")
        print("  python3 pipeline_config.py 4  # Debug mode")
        print("  python3 pipeline_config.py 5  # Custom config")
        print("  python3 pipeline_config.py 6  # Save/load config")
        print("="*70)
