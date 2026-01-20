import json
import os
from pathlib import Path
from typing import Any

def combine_batch_files(directory: str, base_name: str) -> None:
    """
    Combine markdown and JSON metadata files from batch processing.
    
    Args:
        directory: Directory containing the batch files
        base_name: Base name of the files (e.g., 'LotNR')
    """
    dir_path = Path(directory)
    
    # Find all batch files and read their metadata to sort by page range
    batch_info: list[tuple[int, Path, Path]] = []  # (min_page, md_file, json_file)
    
    for file in dir_path.iterdir():
        if file.name.startswith(f"{base_name}_") and file.suffix == ".md":
            # Find corresponding JSON file
            json_file = dir_path / file.name.replace(".md", "_meta.json")
            if json_file.exists():
                try:
                    # Read JSON to get page range
                    with open(json_file, "r", encoding="utf-8") as f:
                        batch_metadata = json.load(f)
                    page_stats = batch_metadata.get("page_stats", [])
                    if page_stats:
                        page_ids = [stat.get("page_id") for stat in page_stats if stat.get("page_id") is not None]
                        if page_ids:
                            min_page = min(page_ids)
                            batch_info.append((min_page, file, json_file))
                        else:
                            # No valid page IDs, use filename-based batch number as fallback
                            try:
                                batch_num = int(file.stem.split("_")[-1])
                                batch_info.append((batch_num * 10000, file, json_file))  # Large offset to avoid conflicts
                            except ValueError:
                                continue
                    else:
                        # No page stats, use filename-based batch number as fallback
                        try:
                            batch_num = int(file.stem.split("_")[-1])
                            batch_info.append((batch_num * 10000, file, json_file))
                        except ValueError:
                            continue
                except Exception as e:
                    print(f"Warning: Could not read {json_file}: {e}")
                    continue
    
    # Sort by minimum page ID in each batch (ensures correct order even with conflicting batch numbers)
    batch_info.sort(key=lambda x: x[0])
    
    md_files = [(info[0], info[1]) for info in batch_info]  # (min_page, md_file)
    json_files = [(info[0], info[2]) for info in batch_info]  # (min_page, json_file)
    
    if not md_files:
        print(f"No batch markdown files found with pattern {base_name}_*.md")
        return
    
    print(f"Found {len(md_files)} markdown batches and {len(json_files)} JSON metadata batches")
    
    # Combine markdown files (sorted by page range)
    combined_md_parts: list[str] = []
    for min_page, md_file in md_files:
        print(f"Reading batch (pages starting at {min_page}): {md_file.name}")
        content = md_file.read_text(encoding="utf-8")
        if content.strip():
            combined_md_parts.append(content.strip())
    
    combined_md = "\n\n".join(combined_md_parts)
    
    # Write combined markdown
    output_md = dir_path / f"{base_name}.md"
    output_md.write_text(combined_md, encoding="utf-8")
    print(f"\nCombined markdown written to: {output_md}")
    print(f"Total size: {len(combined_md)} characters")
    
    # Combine JSON metadata files
    if json_files:
        combined_metadata: dict[str, Any] = {
            "table_of_contents": [],
            "page_stats": [],
            "debug_data_path": f"debug_data\\{base_name}"
        }
        
        all_toc_entries: dict[tuple[int, str], dict[str, Any]] = {}
        all_page_stats: dict[int, dict[str, Any]] = {}
        pages_from_batches: set[int] = set()
        
        for min_page, json_file in json_files:
            print(f"Reading metadata batch (pages starting at {min_page}): {json_file.name}")
            with open(json_file, "r", encoding="utf-8") as f:
                batch_metadata = json.load(f)
            
            # Merge table of contents (deduplicate by page_id and title)
            if "table_of_contents" in batch_metadata:
                for toc_entry in batch_metadata["table_of_contents"]:
                    page_id = toc_entry.get("page_id")
                    title = toc_entry.get("title", "")
                    key = (page_id, title)
                    if key not in all_toc_entries:
                        all_toc_entries[key] = toc_entry
            
            # Merge page stats (deduplicate by page_id) - preserve all pages
            if "page_stats" in batch_metadata:
                for page_stat in batch_metadata["page_stats"]:
                    page_id = page_stat.get("page_id")
                    if page_id is not None:
                        pages_from_batches.add(page_id)
                        # If duplicate page_id exists, keep the first one (or could keep last)
                        if page_id not in all_page_stats:
                            all_page_stats[page_id] = page_stat
                        else:
                            # Warn about duplicates but keep first
                            print(f"  WARNING: Duplicate page_id {page_id} found in {json_file.name}")
        
        # Convert to sorted lists
        combined_metadata["table_of_contents"] = sorted(
            list(all_toc_entries.values()),
            key=lambda x: (x.get("page_id", 0), x.get("title", ""))
        )
        combined_metadata["page_stats"] = sorted(
            list(all_page_stats.values()),
            key=lambda x: x.get("page_id", 0)
        )
        
        # Verify all pages from batches are included
        pages_in_combined = {stat.get("page_id") for stat in combined_metadata["page_stats"] if stat.get("page_id") is not None}
        missing_pages = pages_from_batches - pages_in_combined
        
        if missing_pages:
            print(f"\nERROR: {len(missing_pages)} pages from batches are missing in combined output!")
            print(f"Missing page IDs: {sorted(missing_pages)}")
        
        # Check for gaps in page coverage
        if combined_metadata["page_stats"]:
            page_ids = [stat.get("page_id") for stat in combined_metadata["page_stats"] if stat.get("page_id") is not None]
            if page_ids:
                min_page = min(page_ids)
                max_page = max(page_ids)
                expected_pages = set(range(min_page, max_page + 1))
                actual_pages = set(page_ids)
                missing_in_range = sorted(expected_pages - actual_pages)
                
                if missing_in_range:
                    print(f"\nWARNING: Gaps detected in page range {min_page}-{max_page}")
                    if len(missing_in_range) <= 20:
                        print(f"Missing pages in range: {missing_in_range}")
                    else:
                        print(f"Missing pages in range: {missing_in_range[:20]}... ({len(missing_in_range)} total)")
                
                if min_page > 0:
                    print(f"\nNOTE: Combined output starts at page {min_page}, pages 0-{min_page-1} are missing")
                    print(f"      These pages were not processed in any batch and need to be converted separately")
        
        # Write combined JSON
        output_json = dir_path / f"{base_name}_meta.json"
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(combined_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\nCombined metadata written to: {output_json}")
        print(f"Total TOC entries: {len(combined_metadata['table_of_contents'])}")
        print(f"Total page stats: {len(combined_metadata['page_stats'])}")
        if page_ids:
            print(f"Page range: {min_page} - {max_page}")
    else:
        print("\nNo JSON metadata files found to combine")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python combine_batches.py <directory> [base_name]")
        print("Example: python combine_batches.py Books/LotNR LotNR")
        sys.exit(1)
    
    directory = sys.argv[1]
    base_name = sys.argv[2] if len(sys.argv) > 2 else "LotNR"
    
    combine_batch_files(directory, base_name)
