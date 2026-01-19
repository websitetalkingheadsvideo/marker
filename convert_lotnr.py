"""
Convert Books/LotNR.pdf to Markdown using Marker's recommended workflow.

This script follows the official Marker documentation best practices:
- Uses --use_llm flag for highest accuracy (per README line 28)
- Uses default gemini-2.0-flash model (per README line 28)
- Outputs clean, well-structured Markdown suitable for downstream processing
"""

import os
import time
from pathlib import Path

from marker.config.parser import ConfigParser
from marker.logger import configure_logging, get_logger
from marker.models import create_model_dict
from marker.output import save_output

# Configure logging
configure_logging()
logger = get_logger()

def convert_pdf_to_markdown(
    pdf_path: str,
    output_dir: str | None = None,
    use_llm: bool = True,
    force_ocr: bool = False,
) -> None:
    """
    Convert PDF to Markdown using Marker's recommended workflow.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory for output files (defaults to Marker's default)
        use_llm: Enable LLM processing for highest accuracy (recommended)
        force_ocr: Force OCR on all pages (use if text is garbled)
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    logger.info(f"Starting conversion of {pdf_path.name}...")
    logger.info(f"Using LLM mode: {use_llm}")
    if use_llm:
        logger.info("LLM service: gemini-2.0-flash (default)")
    
    start_time = time.time()
    
    # Create model dictionary (loads Marker's models)
    logger.info("Loading Marker models...")
    models = create_model_dict()
    
    # Configure conversion parameters following Marker best practices
    config_options = {
        "use_llm": use_llm,
        "output_format": "markdown",
        "force_ocr": force_ocr,
    }
    
    if output_dir:
        config_options["output_dir"] = output_dir
    
    # Parse configuration
    config_parser = ConfigParser(config_options)
    
    # Get converter class (default is PdfConverter)
    converter_cls = config_parser.get_converter_cls()
    
    # Create converter with proper configuration
    converter = converter_cls(
        config=config_parser.generate_config_dict(),
        artifact_dict=models,
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
        llm_service=config_parser.get_llm_service(),
    )
    
    # Perform conversion
    logger.info(f"Converting {pdf_path.name}...")
    rendered = converter(str(pdf_path))
    
    # Determine output directory
    out_folder = config_parser.get_output_folder(str(pdf_path))
    base_filename = config_parser.get_base_filename(str(pdf_path))
    
    # Save output (markdown + metadata + images)
    save_output(rendered, out_folder, base_filename)
    
    elapsed_time = time.time() - start_time
    logger.info(f"Conversion complete!")
    logger.info(f"Output saved to: {out_folder}")
    logger.info(f"Base filename: {base_filename}")
    logger.info(f"Total time: {elapsed_time:.2f} seconds")
    
    # Print output file paths
    output_path = Path(out_folder) / f"{base_filename}.md"
    metadata_path = Path(out_folder) / f"{base_filename}_meta.json"
    
    if output_path.exists():
        logger.info(f"Markdown file: {output_path}")
        logger.info(f"File size: {output_path.stat().st_size / 1024:.2f} KB")
    
    if metadata_path.exists():
        logger.info(f"Metadata file: {metadata_path}")

if __name__ == "__main__":
    # Convert Books/LotNR.pdf following Marker best practices
    pdf_file = "Books/LotNR.pdf"
    output_directory = "Books"  # Save output in same directory as PDF
    
    convert_pdf_to_markdown(
        pdf_path=pdf_file,
        output_dir=output_directory,
        use_llm=True,  # Recommended for highest accuracy
        force_ocr=False,  # Set to True if text appears garbled
    )
