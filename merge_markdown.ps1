# Merge markdown from individual page processing
# This assumes we need to reprocess pages 1-100 in batches to get their markdown back

$outputDir = "V:\reference\Books\@Books\MET - VTM - Laws of the Night (Text searchable)"
$finalMd = Join-Path $outputDir "MET - VTM - Laws of the Night (Text searchable).md"
$tempDir = Join-Path $outputDir "_temp_markdown"
$batchDir = Join-Path $outputDir "_batch_markdown"

Write-Host "=== Merging Markdown Files ===" -ForegroundColor Cyan

# Step 1: Reprocess pages 1-100 in batches to get their markdown
Write-Host "`nReprocessing pages 1-100 in batches..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $batchDir -Force | Out-Null

$batches = @()
for($i=1; $i -le 100; $i+=5) {
    $end = [Math]::Min($i+4, 100)
    $batches += "$i-$end"
}

foreach($batch in $batches) {
    Write-Host "Processing batch $batch..."
    $result = marker_single --page_range $batch --paginate_output --output_dir $batchDir "V:\reference\Books\MET - VTM - Laws of the Night (Text searchable).pdf" 2>&1 | Out-Null
    if($LASTEXITCODE -eq 0) {
        $mdFile = Get-ChildItem $batchDir -Filter "*.md" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if($mdFile) {
            $newName = Join-Path $batchDir "batch_$batch.md"
            Copy-Item $mdFile.FullName $newName -Force
            Remove-Item $mdFile.FullName -Force
        }
    }
}

# Step 2: Collect all markdown files
Write-Host "`nCollecting markdown files..." -ForegroundColor Yellow
$allMarkdowns = @()

# Add batch files (pages 1-100)
$batchFiles = Get-ChildItem $batchDir -Filter "batch_*.md" | Sort-Object { 
    $match = $_.BaseName -match 'batch_(\d+)-(\d+)'
    if($match) { [int]$matches[1] } else { 0 }
}
foreach($file in $batchFiles) {
    $content = Get-Content $file.FullName -Raw
    if($content) {
        $allMarkdowns += $content
    }
}

# Add individual page files (pages 101-273) if temp dir exists
if(Test-Path $tempDir) {
    $pageFiles = Get-ChildItem $tempDir -Filter "page_*.md" | Sort-Object { 
        [int]($_.BaseName -replace 'page_', '') 
    }
    foreach($file in $pageFiles) {
        $content = Get-Content $file.FullName -Raw
        if($content) {
            $allMarkdowns += "`n`n$content"
        }
    }
}

# Step 3: Merge and save
Write-Host "`nMerging and saving final markdown..." -ForegroundColor Yellow
$merged = $allMarkdowns -join "`n`n"
Set-Content -Path $finalMd -Value $merged -NoNewline

# Cleanup
Remove-Item $batchDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`n✓ Merged markdown saved to: $finalMd" -ForegroundColor Green
$finalSize = (Get-Item $finalMd).Length
Write-Host "Final size: $([math]::Round($finalSize/1KB, 2)) KB" -ForegroundColor Green
