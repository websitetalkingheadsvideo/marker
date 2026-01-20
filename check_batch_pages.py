import json
from pathlib import Path
from collections import defaultdict

def analyze_batch_pages(directory: str, base_name: str) -> None:
    """Analyze page coverage in batch files."""
    dir_path = Path(directory)
    
    # Find all JSON metadata files
    json_files: list[tuple[int, Path]] = []
    for file in dir_path.iterdir():
        if file.name.startswith(f"{base_name}_") and file.name.endswith("_meta.json"):
            try:
                batch_num = int(file.stem.replace("_meta", "").split("_")[-1])
                json_files.append((batch_num, file))
            except ValueError:
                continue
    
    json_files.sort(key=lambda x: x[0])
    
    print(f"Found {len(json_files)} batch metadata files\n")
    
    all_page_ids: set[int] = set()
    batch_pages: dict[int, list[int]] = {}
    
    for batch_num, json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            batch_metadata = json.load(f)
        
        page_ids = [stat["page_id"] for stat in batch_metadata.get("page_stats", [])]
        batch_pages[batch_num] = sorted(page_ids)
        all_page_ids.update(page_ids)
        
        if page_ids:
            print(f"Batch {batch_num:2d}: pages {min(page_ids):3d}-{max(page_ids):3d} ({len(page_ids)} pages)")
        else:
            print(f"Batch {batch_num:2d}: NO PAGES")
    
    all_pages_sorted = sorted(all_page_ids)
    
    print(f"\n{'='*60}")
    print(f"Total unique pages found: {len(all_page_ids)}")
    if all_pages_sorted:
        print(f"Page range: {all_pages_sorted[0]} - {all_pages_sorted[-1]}")
        print(f"Missing pages: {[p for p in range(all_pages_sorted[0], all_pages_sorted[-1]+1) if p not in all_page_ids]}")
        print(f"Pages before first: {list(range(0, all_pages_sorted[0])) if all_pages_sorted[0] > 0 else 'None'}")

if __name__ == "__main__":
    import sys
    directory = sys.argv[1] if len(sys.argv) > 1 else "Books/LotNR"
    base_name = sys.argv[2] if len(sys.argv) > 2 else "LotNR"
    analyze_batch_pages(directory, base_name)
