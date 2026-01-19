# Process remaining pages (174-273) in 25-page batches
# Larger batches = fewer model loads = faster and more reliable
# Pages 1-173 already processed - starting from 174
$batches = @()
for($i=174; $i -le 273; $i+=25) {
    $end = [Math]::Min($i+24, 273)
    $batches += "$i-$end"
}

$success = 0
$failed = @()
$startTime = Get-Date
$lastUpdateTime = $startTime
$outputDir = "V:\reference\Books\@Books"
$pdfName = "LotNR"
$pdfPath = "V:\reference\Books\LotNR.pdf"
$markdownDir = Join-Path $outputDir $pdfName
$finalMd = Join-Path $markdownDir "$pdfName.md"

# Initialize master markdown file (append to existing if any)
# Don't delete - we're appending to existing content

Write-Host "Processing remaining pages 174-273 in $($batches.Count) batches of ~25 pages each..." -ForegroundColor Cyan
Write-Host "Progress updates: After each batch and every 10 minutes" -ForegroundColor Gray
Write-Host "Using larger batches to reduce model loading overhead" -ForegroundColor Yellow

foreach($batch in $batches) {
    $batchStartTime = Get-Date
    Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] Processing batch $batch ($($success + 1)/$($batches.Count))..." -ForegroundColor Cyan
    
    # Read existing master file content BEFORE marker overwrites it
    $existingContent = ""
    if(Test-Path $finalMd) {
        $existingContent = Get-Content $finalMd -Raw
    }
    
    # Process batch directly to output directory (marker will overwrite the file)
    $result = marker_single --page_range $batch --paginate_output --output_dir $outputDir $pdfPath 2>&1 | Out-Null
    
    if($LASTEXITCODE -eq 0) {
        # Read the markdown that marker just wrote (it overwrote the file)
        $batchMd = Join-Path $markdownDir "$pdfName.md"
        if(Test-Path $batchMd) {
            $newContent = Get-Content $batchMd -Raw
            if($newContent) {
                # Extract first page number from new batch to determine insertion point
                $newFirstPageMatch = [regex]::Match($newContent, '\{(\d+)\}------------------------------------------------')
                $newFirstPage = if($newFirstPageMatch.Success) { [int]$newFirstPageMatch.Groups[1].Value } else { 999 }
                
                # Extract first page number from existing content
                $existingFirstPage = 999
                if($existingContent) {
                    $existingFirstPageMatch = [regex]::Match($existingContent, '\{(\d+)\}------------------------------------------------')
                    if($existingFirstPageMatch.Success) {
                        $existingFirstPage = [int]$existingFirstPageMatch.Groups[1].Value
                    }
                }
                
                # Merge in correct order: if new pages come before existing, prepend; otherwise append
                if($newFirstPage -lt $existingFirstPage) {
                    # New pages should come first
                    $combinedContent = "$newContent`n`n$existingContent"
                } else {
                    # New pages should come after existing
                    $combinedContent = if($existingContent) { "$existingContent`n`n$newContent" } else { $newContent }
                }
                
                Set-Content -Path $finalMd -Value $combinedContent -NoNewline
            }
        }
        $success++
        $batchElapsed = (Get-Date) - $batchStartTime
        
        # Show progress after every batch
        $imageCount = (Get-ChildItem $markdownDir -File -Filter "*.jpeg" -ErrorAction SilentlyContinue | Measure-Object).Count
        $mdSize = if(Test-Path $finalMd) { (Get-Item $finalMd).Length } else { 0 }
        $batchTime = [math]::Round($batchElapsed.TotalSeconds, 1)
        $mdSizeKB = [math]::Round($mdSize/1KB, 1)
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Batch $batch completed in ${batchTime}s | Total: $success/$($batches.Count) batches | Images: $imageCount | MD: ${mdSizeKB} KB" -ForegroundColor Green
        
        # Show detailed update every 10 minutes
        $elapsedSinceUpdate = (Get-Date) - $lastUpdateTime
        if($elapsedSinceUpdate.TotalMinutes -ge 10) {
            $totalElapsed = (Get-Date) - $startTime
            $pagesProcessed = $success * 25
            $pagesRemaining = 273 - $pagesProcessed
            $avgTimePerBatch = $totalElapsed.TotalSeconds / $success
            $estimatedRemaining = [TimeSpan]::FromSeconds($avgTimePerBatch * ($batches.Count - $success))
            
            Write-Host "`n=== 10-Minute Progress Update ===" -ForegroundColor Yellow
            Write-Host "Batches completed: $success/$($batches.Count)" -ForegroundColor Cyan
            $totalPages = 173 + $pagesProcessed
            Write-Host "Pages processed: $totalPages/273 (173 done previously + $pagesProcessed new)" -ForegroundColor Cyan
            Write-Host "Images extracted: $imageCount" -ForegroundColor Cyan
            Write-Host "Markdown size: $([math]::Round($mdSize/1KB, 1)) KB" -ForegroundColor Cyan
            Write-Host "Total elapsed: $([math]::Round($totalElapsed.TotalMinutes, 1)) minutes" -ForegroundColor Cyan
            Write-Host "Estimated remaining: $([math]::Round($estimatedRemaining.TotalMinutes, 1)) minutes" -ForegroundColor Gray
            Write-Host "================================" -ForegroundColor Yellow
            $lastUpdateTime = Get-Date
        }
    } else {
        $failed += $batch
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Batch $batch FAILED" -ForegroundColor Red
        Write-Host "Continuing with next batch..." -ForegroundColor Yellow
    }
}

$elapsed = (Get-Date) - $startTime
Write-Host "`n=== Summary ===" -ForegroundColor Yellow
Write-Host "Successful: $success/$($batches.Count) batches"
Write-Host "Failed batches: $($failed -join ', ')"
Write-Host "Total time: $([math]::Round($elapsed.TotalMinutes, 2)) minutes"
Write-Host ""
Write-Host "Output saved to: $markdownDir" -ForegroundColor Green
