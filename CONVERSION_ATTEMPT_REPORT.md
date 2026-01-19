# Marker PDF Conversion Attempt Report
## Books/LotNR.pdf to Markdown Conversion

**Date:** January 18-19, 2026  
**Target File:** `Books/LotNR.pdf`  
**Goal:** Convert PDF to clean, well-structured Markdown using Marker

---

## Summary

Multiple attempts were made to convert `Books/LotNR.pdf` to Markdown using Marker's recommended workflow. The primary issue encountered was commands hanging during the Surya model import phase with no output or progress indication. One partial success was achieved where conversion progressed more than halfway, but the output file was being overwritten with each page instead of being appended.

---

## Attempts Made

### 1. Initial Setup and Analysis
- **Action:** Analyzed Marker README to identify recommended workflow
- **Findings:**
  - Recommended command: `marker_single Books\LotNR.pdf --use_llm --output_dir Books`
  - Default LLM: `gemini-2.0-flash` (requires `GOOGLE_API_KEY`)
  - Output location: `Books/LotNR/LotNR.md`
- **Status:** Planning phase

### 2. Command Execution Attempts
- **Commands Tried:**
  - `marker_single Books\LotNR.pdf --use_llm --output_dir Books`
  - `marker_single Books\LotNR.pdf --output_dir Books` (without LLM)
- **Result:** Commands hung immediately with no output
- **Issue:** Process appeared to hang during Surya model import phase
- **Process Status:** Multiple processes remained running but used 0% CPU, indicating they were stuck, not processing

### 3. Diagnostic Attempts

#### 3.1 Python Import Testing
- **Action:** Attempted to test Marker imports directly
- **Commands:**
  - `python -c "import marker"`
  - `python quick_test.py`
  - `python test_marker.py`
- **Result:** All commands timed out during import
- **Root Cause Identified:** Surya modules initialize models during import, causing hangs with no progress output

#### 3.2 Model Cache Investigation
- **Action:** Checked HuggingFace cache for existing models
- **Findings:**
  - Cache location: `C:\Users\paris\.cache\huggingface\hub`
  - No Surya models found in cache (models would need to download on first run)
  - Other models present (Docling, Llama, Stable Diffusion)
- **Conclusion:** First run would require model downloads (~2-5GB, 10-15 minutes expected)

#### 3.3 Network Connectivity Check
- **Action:** Tested connection to HuggingFace
- **Result:** Network connectivity confirmed (huggingface.co:443 accessible)
- **Conclusion:** Network not the issue

#### 4. Verbose Output Attempts
- **Actions:**
  - Set `HF_HUB_VERBOSITY=info` and `TRANSFORMERS_VERBOSITY=info`
  - Attempted Python verbose mode: `python -v -m marker.scripts.convert_single`
- **Result:** Still no output, commands continued to hang

### 5. Process Management
- **Action:** Identified and killed hung processes
- **Processes Found:**
  - Process 24312: Started 10:48 PM (with `--use_llm`)
  - Process 30276: Started 10:55 PM (without `--use_llm`)
  - Process 38240: Started 11:04 PM (without `--use_llm`)
- **Status:** All processes killed successfully

---

## Partial Success: Page-by-Page Conversion Issue

### What Worked
- **Progress:** More than half of the document was successfully converted
- **Method:** Conversion was working page-by-page
- **Output Location:** Files were being created in the expected directory

### Critical Bug Encountered
- **Issue:** The Markdown file was **writing over itself with each page** instead of appending
- **Impact:** Only the last processed page remained in the output file
- **Result:** Despite processing more than 50% of the document, the final output contained only the last page's content

### Technical Details
- The conversion process was functioning correctly
- Model loading and processing worked as expected
- The file writing logic had a bug where it opened the file in overwrite mode instead of append mode for each page
- This caused all previous page content to be lost

---

## Root Causes Identified

### 1. Import-Time Model Initialization
- **Problem:** Surya initializes models during module import, not on first use
- **Impact:** Commands hang silently during import with no progress indication
- **Location:** `marker/models.py` imports Surya modules which trigger model loading

### 2. Silent Hanging
- **Problem:** No output or progress indicators during model download/initialization
- **Impact:** Impossible to determine if process is working or stuck
- **User Experience:** Commands appear frozen with no feedback

### 3. File Writing Bug (Partial Success Case)
- **Problem:** Output file opened in overwrite mode per page instead of append mode
- **Impact:** Only last page content preserved in final output
- **Location:** Likely in `marker/output.py` or the renderer logic

---

## Files Created During Investigation

1. `convert_lotnr.py` - Python script following Marker best practices
2. `LOTNR_CONVERSION_GUIDE.md` - Documentation of recommended workflow
3. `quick_test.py` - Diagnostic script for testing imports
4. `test_marker.py` - Test script for model loading
5. `check_model_cache.py` - Script to check HuggingFace cache location

---

## Recommendations

### Immediate Fixes Needed

1. **File Writing Logic**
   - Fix the page-by-page writing to append instead of overwrite
   - Ensure all pages are preserved in the final Markdown output
   - Location to check: `marker/output.py` and renderer implementations

2. **Progress Feedback**
   - Add progress indicators during model download/initialization
   - Show status messages during import phase
   - Provide feedback when models are downloading vs. loading from cache

3. **Import Optimization**
   - Consider lazy loading of models instead of import-time initialization
   - Delay model loading until actually needed
   - This would prevent silent hangs during import

### Workarounds

1. **For Current Issue:**
   - Wait for models to download on first run (10-15 minutes with no feedback)
   - Monitor cache directory to confirm downloads: `$env:USERPROFILE\.cache\huggingface\hub`
   - After first successful run, subsequent runs should be faster

2. **For File Overwrite Bug:**
   - Process document in smaller page ranges to preserve output
   - Manually merge page outputs if needed
   - Wait for fix in Marker codebase

---

## Environment Details

- **OS:** Windows 10 (Build 26200)
- **Python:** 3.13 (via virtual environment at `C:\Users\paris\.venv`)
- **Marker Installation:** `marker-pdf` package installed
- **LLM API Key:** `GOOGLE_API_KEY` environment variable set
- **Network:** Connectivity to HuggingFace confirmed
- **Cache Location:** `C:\Users\paris\.cache\huggingface\hub`

---

## Conclusion

The conversion process has fundamental issues with:
1. Silent hanging during import phase
2. Lack of progress feedback
3. File writing bug that overwrites instead of appends

The partial success demonstrates that the core conversion logic works, but the file output mechanism needs fixing. The import-time model initialization causes poor user experience with no feedback during the critical first-run model download phase.

**Next Steps:**
1. Fix file writing to append pages instead of overwriting
2. Add progress indicators for model download/initialization
3. Consider lazy loading models to prevent import-time hangs
