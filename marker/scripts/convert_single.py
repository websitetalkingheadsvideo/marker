import os

os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = (
    "1"  # Transformers uses .isin for a simple op, which is not supported on MPS
)

import time
import sys
import click

from marker.config.parser import ConfigParser
from marker.config.printer import CustomClickPrinter
from marker.logger import configure_logging, get_logger
from marker.models import create_model_dict
from marker.output import save_output

configure_logging()
logger = get_logger()


@click.command(cls=CustomClickPrinter, help="Convert a single PDF to markdown.")
@click.argument("fpath", type=str)
@ConfigParser.common_options
def convert_single_cli(fpath: str, **kwargs):
    models = create_model_dict()
    start = time.time()
    config_parser = ConfigParser(kwargs)

    converter_cls = config_parser.get_converter_cls()
    config_dict = config_parser.generate_config_dict()
    converter = converter_cls(
        config=config_dict,
        artifact_dict=models,
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
        llm_service=config_parser.get_llm_service(),
    )
    rendered = converter(fpath)
    out_folder = config_parser.get_output_folder(fpath)
    fname_base = config_parser.get_base_filename(fpath)
    
    # Write debug file BEFORE save_output to confirm we get here
    debug_file = os.path.join(out_folder, "_rename_debug.txt")
    with open(debug_file, "w") as f:
        f.write(f"Code executed before save_output\n")
        f.write(f"out_folder: {out_folder}\n")
        f.write(f"fname_base: {fname_base}\n")
        f.write(f"config_dict keys: {list(config_dict.keys())}\n")
        f.write(f"page_range from config_dict: {config_dict.get('page_range')}\n")
    
    # Save with original filename first
    save_output(rendered, out_folder, fname_base)
    
    # If page_range is provided, rename the file to include page range (e.g., LotNR_0-4.md)
    try:
        page_range_list = config_dict.get("page_range")
        with open(debug_file, "a") as f:
            f.write(f"page_range_list: {page_range_list}\n")
            f.write(f"is_list: {isinstance(page_range_list, list) if page_range_list else False}\n")
            f.write(f"len: {len(page_range_list) if page_range_list and isinstance(page_range_list, list) else 0}\n")
        logger.info(f"DEBUG: page_range_list from config_dict: {page_range_list}")
        if page_range_list and isinstance(page_range_list, list) and len(page_range_list) > 0:
            with open(debug_file, "a") as f:
                f.write(f"Entered if block - will rename\n")
            min_page = min(page_range_list)
            max_page = max(page_range_list)
            new_fname_base = f"{fname_base}_{min_page}-{max_page}"
            
            # Rename the markdown file
            old_md_path = os.path.join(out_folder, f"{fname_base}.md")
            new_md_path = os.path.join(out_folder, f"{new_fname_base}.md")
            logger.info(f"DEBUG: Attempting rename from {old_md_path} to {new_md_path}")
            logger.info(f"DEBUG: old_md_path exists: {os.path.exists(old_md_path)}")
            if os.path.exists(old_md_path) and old_md_path != new_md_path:
                os.rename(old_md_path, new_md_path)
                logger.info(f"Renamed output file to {new_fname_base}.md")
            else:
                logger.info(f"DEBUG: Rename skipped - old exists: {os.path.exists(old_md_path)}, paths equal: {old_md_path == new_md_path}")
            
            # Rename the metadata file
            old_meta_path = os.path.join(out_folder, f"{fname_base}_meta.json")
            new_meta_path = os.path.join(out_folder, f"{new_fname_base}_meta.json")
            if os.path.exists(old_meta_path) and old_meta_path != new_meta_path:
                os.rename(old_meta_path, new_meta_path)
                logger.info(f"Renamed metadata file to {new_fname_base}_meta.json")
        else:
            logger.info(f"DEBUG: No rename - page_range_list: {page_range_list}, is_list: {isinstance(page_range_list, list) if page_range_list else False}")
    except Exception as e:
        logger.error(f"Error during file renaming: {e}")
        import traceback
        logger.error(traceback.format_exc())

    logger.info(f"Saved markdown to {out_folder}")
    logger.info(f"Total time: {time.time() - start}")
