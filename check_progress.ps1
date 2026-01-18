# Quick progress check
$imageCount = (Get-ChildItem "V:\reference\Books\@Books\MET - VTM - Laws of the Night (Text searchable)" -File -Filter "*.jpeg" | Measure-Object).Count
$mdSize = (Get-ChildItem "V:\reference\Books\@Books\MET - VTM - Laws of the Night (Text searchable)" -File -Filter "*.md" | Measure-Object -Property Length -Sum).Sum

Write-Host "=== Progress Update ===" -ForegroundColor Cyan
Write-Host "Images extracted: $imageCount"
Write-Host "Markdown size: $([math]::Round($mdSize/1KB, 2)) KB"
Write-Host "Time: $(Get-Date -Format 'HH:mm:ss')"
