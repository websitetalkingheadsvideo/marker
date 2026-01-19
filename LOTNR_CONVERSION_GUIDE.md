# Converting Books/LotNR.pdf to Markdown with Marker

## Recommended Workflow (Per Marker Documentation)

Based on the official Marker README, here's the optimal workflow for converting `Books/LotNR.pdf` to clean, well-structured Markdown.

## Step 1: Verify Prerequisites

1. **Marker is installed**: `pip install marker-pdf`
2. **LLM API Key is configured**: 
   - `GOOGLE_API_KEY` environment variable is set (✓ verified)
   - Or pass `--gemini_api_key YOUR_KEY` to commands

## Step 2: Choose Conversion Method

### Option A: Command-Line (Recommended for Quick Conversion)

```powershell
# Basic conversion (fast, good quality)
marker_single Books\LotNR.pdf --output_dir Books

# Highest accuracy conversion (uses LLM, recommended per README line 28)
marker_single Books\LotNR.pdf --use_llm --output_dir Books

# If text appears garbled, force OCR
marker_single Books\LotNR.pdf --use_llm --force_ocr --output_dir Books
```

### Option B: Python Script (Better Control & Error Handling)

Run the provided script:
```powershell
python convert_lotnr.py
```

## Step 3: Output Files

Marker will create the following files in the output directory:

- `LotNR.md` - The main Markdown output
- `LotNR_meta.json` - Metadata (table of contents, page stats, etc.)
- `LotNR_images/` - Extracted images (if any)

## Configuration Decisions & Assumptions

### LLM Usage (`--use_llm`)
**Decision**: ✅ **Enabled** (recommended)
- **Rationale**: README line 28 states "For the highest accuracy, pass the `--use_llm` flag"
- **Benefits**: 
  - Merges tables across pages
  - Handles inline math properly
  - Formats tables correctly
  - Extracts values from forms
  - Higher accuracy than marker alone (per README benchmarks)

### LLM Service
**Decision**: ✅ **Gemini 2.0 Flash** (default)
- **Rationale**: README line 28 states "By default, it uses `gemini-2.0-flash`"
- **Configuration**: Uses `GOOGLE_API_KEY` environment variable (already set)
- **Alternative services** (if needed):
  - Ollama (local): `--llm_service marker.services.ollama.OllamaService`
  - Claude: `--llm_service marker.services.claude.ClaudeService --claude_api_key KEY`
  - OpenAI: `--llm_service marker.services.openai.OpenAIService --openai_api_key KEY`

### OCR Usage (`--force_ocr`)
**Decision**: ⚠️ **Conditional** (disabled by default)
- **When to enable**: If text appears garbled or PDF has bad text extraction
- **Rationale**: README line 85 states "Some PDFs, even digital ones, have bad text in them"
- **Note**: Also formats inline math to LaTeX when enabled

### Output Format
**Decision**: ✅ **Markdown** (default)
- **Rationale**: Primary use case is Markdown output
- **Alternatives**: `--output_format json`, `--output_format html`, `--output_format chunks`

### Output Directory
**Decision**: ✅ **Books/** (same as source PDF)
- **Rationale**: Keeps output organized with source files
- **Default**: Marker uses `conversion_results/` if not specified

## Expected Output Quality

Per Marker documentation, the Markdown output will include:

✅ **Structure Preservation**
- Headings (h1, h2, etc.) with proper hierarchy
- Lists (ordered and unordered)
- Sections and subsections

✅ **Content Formatting**
- Formatted tables (properly merged across pages with `--use_llm`)
- Embedded LaTeX equations (fenced with `$$`)
- Code blocks (fenced with triple backticks)
- Superscripts for footnotes
- Image links (images saved in same folder)

✅ **Clean Output**
- Headers/footers removed
- Artifacts cleaned
- Proper reading order

## Performance Expectations

- **Time**: Varies by document size and LLM usage
  - Without LLM: ~0.18 seconds per page (per README benchmarks)
  - With LLM: Additional time for API calls (depends on document complexity)
- **VRAM**: ~3.5GB average, ~5GB peak per worker
- **First Run**: May take longer due to model downloads

## Troubleshooting

### If conversion fails or times out:
1. **Check API key**: Verify `GOOGLE_API_KEY` is set correctly
2. **Try without LLM first**: Remove `--use_llm` flag to test basic conversion
3. **Force OCR**: Add `--force_ocr` if text appears garbled
4. **Check device**: Set `TORCH_DEVICE=cuda` if you have GPU, or `TORCH_DEVICE=cpu` to force CPU
5. **Reduce workers**: If out of memory, decrease worker count

### If output quality is poor:
1. **Enable LLM**: Add `--use_llm` flag (if not already enabled)
2. **Force OCR**: Add `--force_ocr` flag
3. **Enable inline math**: Use `--redo_inline_math` with `--use_llm` for best math formatting

## Exact Command for This Document

```powershell
# Recommended command (highest accuracy)
marker_single Books\LotNR.pdf --use_llm --output_format markdown --output_dir Books

# Alternative: Using Python script
python convert_lotnr.py
```

## Notes

- The conversion may take several minutes for large PDFs, especially with LLM enabled
- First run will download models (~few GB) which takes additional time
- Output will be saved as `Books/LotNR.md` with metadata in `Books/LotNR_meta.json`
- Images (if any) will be in `Books/LotNR_images/` directory
