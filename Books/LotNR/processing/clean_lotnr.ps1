# Deterministic text cleaning script for LotNR.md
# Only deletes lines, never modifies kept lines or inserts placeholders

$inputFile = "LotNR.md"
$outputFile = "LotNR.cleaned.md"
$logFile = "LotNR.cleaned.log.txt"
$backupFile = "LotNR.original.md"

# Initialize counters
$totalInputLines = 0
$totalOutputLines = 0
$rule1Count = 0  # Image placeholders
$rule2Count = 0  # Repeated words
$rule3Count = 0  # "of the" runaway
$rule4Count = 0  # Consecutive duplicate headings

# Create backup if it doesn't exist
if (-not (Test-Path $backupFile)) {
    Copy-Item -Path $inputFile -Destination $backupFile
}

# Read file and detect line endings
$fileContent = [System.IO.File]::ReadAllText((Resolve-Path $inputFile).Path)
$lineEnding = "`r`n"  # Default to CRLF
if ($fileContent -match "`r`n") {
    $lineEnding = "`r`n"
} elseif ($fileContent -match "`n") {
    $lineEnding = "`n"
}

# Split into lines (normalize for processing, but we'll use original line ending when writing)
$lineArray = $fileContent -split "`r?`n"
$totalInputLines = $lineArray.Count

# Track previous line for Rule 4
$previousLine = $null
$previousLineIsHeading = $false
$previousHeadingText = $null

# Process each line
$outputLines = @()
foreach ($line in $lineArray) {
    $shouldDelete = $false
    $deletedByRule = 0
    
    # Rule 1: Remove image placeholder lines
    # Pattern: ^\s*!\[\]\(_page_\d+_Picture_\d+\.jpe?g\)\s*$
    if ($line -match '^\s*!\[\]\(_page_\d+_Picture_\d+\.jpe?g\)\s*$') {
        $shouldDelete = $true
        $deletedByRule = 1
        $rule1Count++
    }
    
    # Rule 2: Remove runaway repeated-word lines (4+ times)
    # Pattern: word repeated 4+ times separated by spaces
    if (-not $shouldDelete -and $line -match '\b([A-Za-z]{2,})\s+\1\s+\1\s+\1') {
        $shouldDelete = $true
        $deletedByRule = 2
        $rule2Count++
    }
    
    # Rule 3: Remove "of the" runaway lines (3+ times, case-insensitive)
    # Pattern: "of the" repeated 3+ times
    if (-not $shouldDelete -and $line -imatch '(of the).*(of the).*(of the)') {
        $shouldDelete = $true
        $deletedByRule = 3
        $rule3Count++
    }
    
    # Rule 4: Remove exact duplicate consecutive headings only
    # Both must be headings and trimmed text must be exactly identical
    $currentLineIsHeading = $false
    $currentHeadingText = $null
    
    if (-not $shouldDelete) {
        if ($line -match '^(#+)\s+(.+)$') {
            $currentLineIsHeading = $true
            $currentHeadingText = $matches[2].Trim()
        }
        
        if ($currentLineIsHeading -and $previousLineIsHeading) {
            if ($currentHeadingText -eq $previousHeadingText -and $currentHeadingText -ne '') {
                $shouldDelete = $true
                $deletedByRule = 4
                $rule4Count++
            }
        }
    }
    
    # Keep the line if not deleted
    if (-not $shouldDelete) {
        $outputLines += $line
        $totalOutputLines++
        
        # Update previous line tracking for Rule 4 (only for kept lines)
        $previousLine = $line
        $previousLineIsHeading = $currentLineIsHeading
        if ($currentLineIsHeading) {
            $previousHeadingText = $currentHeadingText
        } else {
            $previousHeadingText = $null
        }
    }
    # If deleted, don't update previous line - next line will compare against last kept line
}

# Write output file (preserving original line endings)
$outputContent = $outputLines -join $lineEnding
$outputPath = Join-Path (Resolve-Path ".").Path $outputFile
[System.IO.File]::WriteAllText($outputPath, $outputContent, [System.Text.Encoding]::UTF8)

# Write log file with counts only
$logContent = @"
$totalInputLines
$totalOutputLines
$rule1Count
$rule2Count
$rule3Count
$rule4Count
"@

$logPath = Join-Path (Resolve-Path ".").Path $logFile
[System.IO.File]::WriteAllText($logPath, $logContent, [System.Text.Encoding]::UTF8)
