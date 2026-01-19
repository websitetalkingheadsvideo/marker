import os

os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = (
    "1"  # Transformers uses .isin for a simple op, which is not supported on MPS
)

import time
import sys
import click
import pypdfium2 as pdfium

from marker.config.parser import ConfigParser
from marker.config.printer import CustomClickPrinter
from marker.logger import configure_logging, get_logger
from marker.models import create_model_dict
from marker.output import save_output

configure_logging()
logger = get_logger()


@click.command(cls=CustomClickPrinter, help="Convert a single PDF to markdown.")
@click.argument("fpath", type=str)
@click.option(
    "--batch_size",
    type=int,
    default=10,
    help="Number of pages to process per batch. If page_range is larger, it will be split into batches.",
)
@ConfigParser.common_options
def convert_single_cli(fpath: str, batch_size: int, **kwargs):
    models = create_model_dict()
    start = time.time()
    config_parser = ConfigParser(kwargs)

    # Get total page count
    doc = pdfium.PdfDocument(fpath)
    try:
        total_pages = len(doc)
    finally:
        doc.close()

    converter_cls = config_parser.get_converter_cls()
    config_dict = config_parser.generate_config_dict()
    out_folder = config_parser.get_output_folder(fpath)
    fname_base = config_parser.get_base_filename(fpath)

    # Determine pages to process
    page_range_list = config_dict.get("page_range")
    if page_range_list and isinstance(page_range_list, list) and len(page_range_list) > 0:
        pages_to_process = sorted(page_range_list)
    else:
        pages_to_process = list(range(total_pages))

    # Split into batches
    batches: list[list[int]] = []
    for i in range(0, len(pages_to_process), batch_size):
        batch = pages_to_process[i : i + batch_size]
        batches.append(batch)

    # Process each batch
    for batch_idx, batch_pages in enumerate(batches):
        logger.info(f"Processing batch {batch_idx + 1}/{len(batches)} (pages {min(batch_pages)}-{max(batch_pages)})")
        
        # Create config for this batch
        batch_config = config_dict.copy()
        batch_config["page_range"] = batch_pages
        
        # Create converter for this batch
        converter = converter_cls(
            config=batch_config,
            artifact_dict=models,
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
            llm_service=config_parser.get_llm_service(),
        )
        
        # Process batch
        rendered = converter(fpath)
        
        # Save with incrementing number
        batch_fname_base = f"{fname_base}_{batch_idx}"
        save_output(rendered, out_folder, batch_fname_base)
        logger.info(f"Saved batch {batch_idx + 1} to {batch_fname_base}.md")

    logger.info(f"Saved {len(batches)} batch(es) to {out_folder}")
    logger.info(f"Total time: {time.time() - start}")
