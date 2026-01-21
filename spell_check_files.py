#!/usr/bin/env python3
"""Spell check markdown files with custom vocabulary support."""

import re
from pathlib import Path
from typing import Set, List, Tuple
from collections import defaultdict

try:
    from spellchecker import SpellChecker
except ImportError:
    print("Error: pyspellchecker is required. Install it with: pip install pyspellchecker")
    exit(1)


def extract_custom_vocabulary(vocab_file: Path) -> Set[str]:
    """Extract words from the WoD vocabulary file."""
    custom_words: Set[str] = set()
    
    if not vocab_file.exists():
        print(f"Warning: Vocabulary file {vocab_file} not found")
        return custom_words
    
    with open(vocab_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract words from markdown list items
    # Match lines starting with "- " followed by text
    pattern = r"^-\s+(.+?)$"
    for match in re.finditer(pattern, content, re.MULTILINE):
        word_text = match.group(1).strip()
        
        # Remove markdown code blocks if present
        word_text = re.sub(r"^`+|`+$", "", word_text)
        
        # Split compound words (like "Blood bond" or "BlackHand")
        # Add both the full form and individual words
        words = re.findall(r'\b[A-Za-z]+\b', word_text)
        for word in words:
            if len(word) > 1:  # Ignore single characters
                custom_words.add(word.lower())
                custom_words.add(word)  # Preserve case variations
    
    return custom_words


def extract_words_from_text(text: str) -> List[Tuple[str, int, str]]:
    """
    Extract words from text, preserving line numbers and context.
    Returns list of (word, line_number, line_context) tuples.
    """
    words: List[Tuple[str, int, str]] = []
    lines = text.split('\n')
    
    for line_num, line in enumerate(lines, start=1):
        # Skip markdown code blocks
        if line.strip().startswith('```'):
            continue
        
        # Skip URLs
        line_without_urls = re.sub(r'https?://\S+', '', line)
        # Skip markdown links [text](url)
        line_without_urls = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', line_without_urls)
        # Skip inline code
        line_without_code = re.sub(r'`[^`]+`', '', line_without_urls)
        
        # Extract words (alphanumeric sequences with at least one letter)
        word_pattern = r'\b[A-Za-z]+[A-Za-z0-9]*\b'
        for match in re.finditer(word_pattern, line_without_code):
            word = match.group(0)
            if len(word) > 1:  # Ignore single character words
                words.append((word, line_num, line.strip()))
    
    return words


def spell_check_file(file_path: Path, custom_vocab: Set[str]) -> List[Tuple[str, int, str, str]]:
    """
    Spell check a file and return list of errors.
    Returns list of (word, line_number, line_context, suggestion) tuples.
    """
    if not file_path.exists():
        return []
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    spell = SpellChecker()
    
    # Add custom vocabulary to the spell checker
    for word in custom_vocab:
        spell.word_frequency.add(word.lower())
    
    words = extract_words_from_text(content)
    errors: List[Tuple[str, int, str, str]] = []
    
    seen_errors: Set[Tuple[str, int]] = set()  # Track (word_lower, line) to avoid duplicates
    
    for word, line_num, line_context in words:
        word_lower = word.lower()
        
        # Skip if already seen on this line
        if (word_lower, line_num) in seen_errors:
            continue
        
        # Skip if in custom vocabulary (case-insensitive check)
        if word_lower in {w.lower() for w in custom_vocab}:
            continue
        
        # Skip common proper nouns (all caps or title case)
        if word.isupper() and len(word) > 1:
            continue
        
        # Check spelling
        if word_lower not in spell:
            # Get suggestion
            candidates = spell.candidates(word_lower)
            if candidates is None:
                candidates = set()
            suggestion = ", ".join(list(candidates)[:3]) if candidates else "No suggestion"
            
            # Double-check: if the word itself is a candidate, it might be valid
            if word_lower in candidates:
                continue
            
            errors.append((word, line_num, line_context, suggestion))
            seen_errors.add((word_lower, line_num))
    
    return errors


def main():
    """Main function to run spell check."""
    base_path = Path(__file__).parent
    
    vocab_file = base_path / "Books" / "wod_vocabulary.md"
    file1 = base_path / "Books" / "LotNR" / "processing" / "LotNR-Headers.md"
    file2 = base_path / "Books" / "wod_vocabulary.md"
    output_file = base_path / "spell_check_results.txt"
    
    print("Extracting custom vocabulary...")
    custom_vocab = extract_custom_vocabulary(vocab_file)
    print(f"Loaded {len(custom_vocab)} custom words from vocabulary file")
    
    output_lines: List[str] = []
    output_lines.append("="*80)
    output_lines.append("Spell checking files...")
    output_lines.append("="*80)
    
    all_errors = {}
    
    for file_path in [file1, file2]:
        if not file_path.exists():
            msg = f"\nWARNING: File not found: {file_path}"
            output_lines.append(msg)
            print(msg)
            continue
        
        print(f"Checking: {file_path.name}...")
        output_lines.append(f"\nChecking: {file_path.name}")
        errors = spell_check_file(file_path, custom_vocab)
        all_errors[file_path] = errors
        
        if errors:
            msg = f"Found {len(errors)} potential spelling errors:"
            output_lines.append(msg)
            
            # Group by word for easier reading
            errors_by_word = defaultdict(list)
            for word, line_num, context, suggestion in errors:
                errors_by_word[word.lower()].append((word, line_num, context, suggestion))
            
            for word_lower, word_errors in sorted(errors_by_word.items()):
                first_error = word_errors[0]
                output_lines.append(f"\n  '{first_error[0]}' appears {len(word_errors)} time(s):")
                for word, line_num, context, suggestion in word_errors[:5]:  # Show first 5 occurrences
                    # Truncate long lines
                    context_display = context if len(context) <= 80 else context[:77] + "..."
                    output_lines.append(f"    Line {line_num}: {context_display}")
                    if suggestion and suggestion != "No suggestion":
                        output_lines.append(f"      -> Suggestions: {suggestion}")
                if len(word_errors) > 5:
                    output_lines.append(f"    ... and {len(word_errors) - 5} more occurrence(s)")
        else:
            msg = "OK: No spelling errors found!"
            output_lines.append(msg)
            print(msg)
    
    output_lines.append("\n" + "="*80)
    output_lines.append("Summary:")
    output_lines.append("="*80)
    total_errors = sum(len(errors) for errors in all_errors.values())
    for file_path, errors in all_errors.items():
        summary_line = f"  {file_path.name}: {len(errors)} potential error(s)"
        output_lines.append(summary_line)
        print(summary_line)
    total_line = f"\nTotal: {total_errors} potential spelling error(s)"
    output_lines.append(total_line)
    print(total_line)
    
    # Write to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    
    print(f"\nFull results saved to: {output_file}")
    
    if total_errors > 0:
        exit(1)


if __name__ == "__main__":
    main()
