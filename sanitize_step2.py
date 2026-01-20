import re
from collections import defaultdict
from pathlib import Path
from typing import List, Tuple, Set

def normalize_for_comparison(line: str) -> str:
    normalized = re.sub(r'[^\w\s]', '', line.lower())
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

def is_near_duplicate(line1: str, line2: str) -> bool:
    norm1 = normalize_for_comparison(line1)
    norm2 = normalize_for_comparison(line2)
    if norm1 == norm2:
        return True
    if abs(len(norm1) - len(norm2)) / max(len(norm1), len(norm2), 1) > 0.2:
        return False
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    if not words1 or not words2:
        return False
    overlap = len(words1 & words2) / max(len(words1), len(words2))
    return overlap > 0.8

def has_runaway_repetition(line: str) -> bool:
    words = line.split()
    if not words:
        return False
    
    word_counts = defaultdict(int)
    for word in words:
        word_counts[word.lower()] += 1
    
    for word, count in word_counts.items():
        if count >= 4:
            return True
    
    if len(words) >= 3:
        for i in range(len(words) - 2):
            phrase = ' '.join(words[i:i+3]).lower()
            remaining = line.lower()[line.lower().find(phrase) + len(phrase):]
            if remaining.count(phrase) >= 1:
                return True
    
    if len(words) >= 5:
        repeated_count = max(word_counts.values())
        if repeated_count > 0 and (repeated_count / len(words)) > 0.6:
            return True
    
    return False

def is_legitimate_section_title(line: str) -> bool:
    stripped = line.strip()
    if 'Chapter' in stripped or 'Contents' in stripped:
        return True
    words = stripped.split()
    if len(words) <= 6 and stripped[0].isupper():
        return True
    return False

def sanitize_document(input_path: str, output_path: str, report_path: str) -> None:
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    original_count = len(lines)
    keep_mask = [True] * len(lines)
    
    stats = {
        'rule1_exact': 0,
        'rule2_near': 0,
        'rule3_runaway': 0,
        'rule4_boilerplate': 0
    }
    
    removed_signatures = defaultdict(int)
    WINDOW_SIZE = 30
    
    for i in range(len(lines)):
        if not keep_mask[i]:
            continue
        
        line = lines[i].rstrip('\n\r')
        stripped = line.strip()
        
        if not stripped:
            continue
        
        trimmed = stripped
        
        if has_runaway_repetition(stripped):
            keep_mask[i] = False
            stats['rule3_runaway'] += 1
            removed_signatures[stripped[:80]] += 1
            continue
        
        window_start = max(0, i - WINDOW_SIZE)
        window_end = min(len(lines), i + WINDOW_SIZE + 1)
        
        found_exact = False
        found_near = False
        
        for j in range(window_start, i):
            if not keep_mask[j]:
                continue
            
            other_line = lines[j].rstrip('\n\r')
            other_stripped = other_line.strip()
            
            if not other_stripped:
                continue
            
            if normalize_for_comparison(stripped) == normalize_for_comparison(other_stripped):
                if not is_legitimate_section_title(stripped):
                    keep_mask[i] = False
                    stats['rule1_exact'] += 1
                    removed_signatures[stripped[:80]] += 1
                    found_exact = True
                    break
            
            if not found_exact and is_near_duplicate(stripped, other_stripped):
                if not is_legitimate_section_title(stripped):
                    keep_mask[i] = False
                    stats['rule2_near'] += 1
                    removed_signatures[stripped[:80]] += 1
                    found_near = True
                    break
        
        if found_exact or found_near:
            continue
    
    line_occurrences = defaultdict(list)
    for i, line in enumerate(lines):
        if keep_mask[i]:
            stripped = line.strip()
            if stripped:
                line_occurrences[stripped].append(i)
    
    for line_text, positions in line_occurrences.items():
        if len(positions) >= 5:
            words = line_text.split()
            if len(words) <= 8:
                normalized = normalize_for_comparison(line_text)
                if not re.search(r'[.!?]$', line_text) and len(normalized.split()) <= 8:
                    if 'Chapter' not in line_text and 'Contents' not in line_text:
                        for pos in positions[1:]:
                            if keep_mask[pos]:
                                keep_mask[pos] = False
                                stats['rule4_boilerplate'] += 1
                                removed_signatures[line_text[:80]] += 1
    
    output_lines = []
    for i, line in enumerate(lines):
        if keep_mask[i]:
            output_lines.append(line)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    removed_count = original_count - len(output_lines)
    
    top_removed = sorted(removed_signatures.items(), key=lambda x: x[1], reverse=True)[:10]
    
    output_filename = Path(output_path).name
    report_filename = Path(report_path).name
    
    report_lines = [
        "# Step 2 Sanitization Report\n\n",
        f"**Input:** `{Path(input_path).name}`\n",
        f"**Output:** [{output_filename}]({output_filename})\n",
        f"**Report:** [{report_filename}]({report_filename})\n\n",
        f"**Total lines removed:** {removed_count}\n\n",
        "## Removal by Rule\n\n",
        f"- Rule 1 (Exact repeated lines): {stats['rule1_exact']}\n",
        f"- Rule 2 (Near-duplicate lines): {stats['rule2_near']}\n",
        f"- Rule 3 (Runaway repetition): {stats['rule3_runaway']}\n",
        f"- Rule 4 (Global boilerplate): {stats['rule4_boilerplate']}\n\n",
        "## Top 10 Removed Line Signatures\n\n"
    ]
    
    for sig, count in top_removed:
        report_lines.append(f"1. `{sig}...` (removed {count} times)\n")
    
    report_lines.append("\n## Before/After Excerpts\n\n")
    
    excerpt_count = 0
    for i in range(min(100, len(lines))):
        if not keep_mask[i] and excerpt_count < 3:
            start = max(0, i - 5)
            end = min(len(lines), i + 6)
            
            report_lines.append(f"### Excerpt {excerpt_count + 1}\n\n")
            report_lines.append("**Before (lines {}-{}):**\n\n".format(start+1, end))
            
            for j in range(start, end):
                marker = "❌" if j == i else ""
                report_lines.append(f"{j+1:5d} {marker} {lines[j]}")
            
            report_lines.append("\n**After:**\n\n")
            
            for j in range(start, end):
                if keep_mask[j]:
                    report_lines.append(f"{j+1:5d} ✓ {lines[j]}")
            
            report_lines.append("\n")
            excerpt_count += 1
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.writelines(report_lines)
    
    print(f"Sanitization complete: {removed_count} lines removed")
    print(f"Output: {output_path}")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    input_file = "Books/LotNR/LotNR.md"
    output_file = "Books/LotNR/LotNR.step2_deduped.md"
    report_file = "Books/LotNR/LotNR.step2_report.md"
    
    sanitize_document(input_file, output_file, report_file)
