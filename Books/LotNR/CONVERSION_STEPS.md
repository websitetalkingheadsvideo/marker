# LotNR Document Conversion Steps

This document outlines the successful conversion pipeline used to process the LotNR PDF into clean, normalized Markdown format.

## Overview

The conversion was performed in three sequential normalization passes, each handling a specific aspect of OCR error correction and text normalization.

---

## Step 1: Initial Cleaning Pass

**Input**: `LotNR.original.md` (raw OCR output)  
**Output**: `LotNR.cleaned.md`  
**Script**: `clean_lotnr.ps1`

### Purpose
Initial cleanup of raw OCR output to remove common errors and artifacts.

### Process
- Removed OCR artifacts and common errors
- Basic text normalization
- Preserved document structure

### Result
Clean base document ready for further normalization passes.

---

## Step 2: Mid-Word Capitalization Fix

**Input**: `LotNR.cleaned.md`  
**Output**: `LotNR.midwordcase_fixed.md`  
**Script**: `fix_midword_case.py` (temporary, removed after use)

### Purpose
Fix OCR-style capitalization errors within words (e.g., "CharaCters" → "Characters").

### Rules Applied
- **Fixed**: Words with capitals in the middle (e.g., "masQuerade" → "Masquerade", "saBBat" → "Sabbat", "oF" → "of")
- **Preserved**: 
  - Proper nouns (correctly capitalized)
  - Acronyms (NPC, ST, USA)
  - Roman numerals
  - Compound words that might be legitimate (e.g., "isMind's" left unchanged to avoid false positives)
- **Conservative approach**: Only fixed when 100% certain

### Examples Fixed
- `masQuerade` → `Masquerade`
- `saBBat` → `Sabbat`
- `seCond` → `Second`
- `CharaCter` → `Character`
- `arChetypes` → `Archetypes`
- `oF` → `of` (when mid-sentence)
- `mindFul` → `Mindful`

### Validation
- Line count preserved exactly (3,397 lines)
- Only letter casing inside words changed
- No words added, removed, merged, or split

---

## Step 3: Heading Title Case Normalization

**Input**: `LotNR.midwordcase_fixed.md`  
**Output**: `LotNR.headings_titlecase.md`  
**Script**: `normalize_headings.py` (temporary, removed after use)

### Purpose
Convert all Markdown headings to proper Title Case following standard conventions.

### Rules Applied

#### Always Capitalize
- First word of heading
- Last word of heading
- All nouns, verbs, adjectives, adverbs, and pronouns

#### Lowercase (unless first/last word)
- Articles: a, an, the
- Conjunctions: and, or, but
- Short prepositions (≤4 letters): of, to, in, on, with, from, over, into

#### Preserved Exactly
- Proper nouns (Vampire, Masquerade, Sabbat, etc.)
- Acronyms (NPC, USA, ST)
- Roman numerals (I, II, III, X, etc.)
- Numbers and punctuation

### Examples Fixed
- `## vampire: the Masquerade and laws of the night` → `## Vampire: the Masquerade and Laws of the Night`
- `# the world of darkness` → `# The World of Darkness`
- `# stories around the Fire` → `# Stories Around the Fire`
- `# the storyteller` → `# The Storyteller`
- `#### THE CAMABILLA` → `#### The Camarilla`

### Validation
- Line count preserved exactly (3,397 lines)
- Only heading lines modified
- Non-heading content unchanged

---

## Step 4: File Organization

**Actions**: Reorganized processed files into subfolders for better structure

### Files Moved to `base/` folder
- All batch markdown files: `LotNR_0.md` through `LotNR_24.md`
- All metadata files: `LotNR_*_meta.json`
- All page images: `_page_*.jpeg` (hundreds of files)
- Original files: `LotNR.md`, `LotNR.original.md`

### Files Moved to `processing/` folder
- `LotNR.cleaned.md`
- `LotNR.midwordcase_fixed.md`
- `LotNR.headings_titlecase.md`
- `LotNR.cleaned.log.txt`
- `clean_lotnr.ps1`
- `LotNR_0_meta.json`

### Result
Clean directory structure with:
- Base files organized in `base/` subfolder
- Processing artifacts in `processing/` subfolder
- Root directory kept minimal

---

## Final Output

**Primary Document**: `Books/LotNR/processing/LotNR.headings_titlecase.md`

This is the final, fully normalized document ready for use, with:
- Clean OCR output
- Fixed mid-word capitalization errors
- Properly formatted heading titles
- Consistent formatting throughout

---

## Key Principles

1. **Sequential Processing**: Each pass builds on the previous output
2. **Conservative Approach**: Only fix errors when certain (avoid false positives)
3. **Preserve Structure**: Never add, remove, merge, or split lines
4. **Line Count Validation**: Ensure exact line count preservation at each step
5. **Minimal Changes**: Only change what needs to be changed

---

## Validation Checklist

After each step:
- [x] Line count matches input exactly
- [x] No lines added or removed
- [x] Only intended changes made
- [x] Proper nouns preserved
- [x] Acronyms preserved
- [x] Document structure intact

---

## Notes

- Temporary scripts (`fix_midword_case.py`, `normalize_headings.py`) were removed after use
- Processing artifacts are preserved in `processing/` folder for reference
- All original files are preserved in `base/` folder
