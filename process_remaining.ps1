# Process entire book (pages 1-273) in 5-page batches
# This approach worked earlier - we got 173 pages of images
# Save directly to output directory - marker will handle file naming
$batches = @()
for($i=1; $i -le 273; $i+=5) {
    $end = [Math]::Min($i+4, 273)
    $batches += "$i-$end"
}

$success = 0
$failed = @()
$startTime = Get-Date
$outputDir = "V:\reference\Books\@Books"

Write-Host "Processing $($batches.Count) batches of 5 pages each..." -ForegroundColor Cyan

foreach($batch in $batches) {
    Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] Processing batch $batch ($($success + 1)/$($batches.Count))..." -ForegroundColor Cyan
    
    # Process batch directly to output directory
    $result = marker_single --page_range $batch --paginate_output --output_dir $outputDir "V:\reference\Books\MET - VTM - Laws of the Night (Text searchable).pdf" 2>&1 | Out-Null
    
    if($LASTEXITCODE -eq 0) {
        $success++
        if($success % 10 -eq 0) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✓ Progress: $success/$($batches.Count) batches completed" -ForegroundColor Green
        }
    } else {
        $failed += $batch
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] ✗ Batch $batch FAILED" -ForegroundColor Red
        Write-Host "Continuing with next batch..." -ForegroundColor Yellow
    }
}

$elapsed = (Get-Date) - $startTime
Write-Host "`n=== Summary ===" -ForegroundColor Yellow
Write-Host "Successful: $success/$($batches.Count) batches"
Write-Host "Failed batches: $($failed -join ', ')"
Write-Host "Total time: $([math]::Round($elapsed.TotalMinutes, 2)) minutes"
Write-Host "`nOutput saved to: $outputDir\MET - VTM - Laws of the Night (Text searchable)\" -ForegroundColor Green
