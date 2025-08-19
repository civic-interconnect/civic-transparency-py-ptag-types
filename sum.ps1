# consolidate-repo.ps1
# Consolidates all repository files into a single document for review
# Run from repository root

param(
    [string]$OutputFile = "repo-consolidation.md"
)

# Directories to include
$IncludeDirs = @(".", ".github",  "docs", "scripts", "src","tests"  )

# Files/patterns to exclude (common artifacts and binaries)
$ExcludePatterns = @(
    "*.pyc", "*.pyo", "*.pyd", "__pycache__", 
    "*.egg-info", "build", "dist", ".git", 
    ".pytest_cache", ".coverage", "htmlcov", "coverage.xml"
    "node_modules", ".venv", "venv", "env",
    "*.log", "*.tmp", "*.temp", "*.cache",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.ico",
    "*.pdf", "*.zip", "*.tar", "*.gz",
    $OutputFile  # Don't include the output file itself
)

Write-Host "Starting file consolidation..." -ForegroundColor Green
Write-Host "Output file: $OutputFile" -ForegroundColor Cyan

# Initialize output
$Content = @()
$Content += "# Repository File Consolidation"
$Content += ""
$Content += "Generated on: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$Content += "Repository root: $(Get-Location)"
$Content += ""
$Content += "---"
$Content += ""

$FileCount = 0

foreach ($Dir in $IncludeDirs) {
    if (Test-Path $Dir) {
        Write-Host "Processing directory: $Dir" -ForegroundColor Yellow
        
        # Get all files recursively, excluding specified patterns
        $Files = Get-ChildItem -Path $Dir -Recurse -File | Where-Object {
            $FilePath = $_.FullName
            $RelativePath = Resolve-Path -Path $FilePath -Relative
            
            # Check if file matches any exclude pattern
            $Exclude = $false
            foreach ($Pattern in $ExcludePatterns) {
                if ($RelativePath -like "*$Pattern*" -or $_.Name -like $Pattern) {
                    $Exclude = $true
                    break
                }
            }
            -not $Exclude
        }
        
        foreach ($File in $Files) {
            try {
                $RelativePath = Resolve-Path -Path $File.FullName -Relative
                $RelativePath = $RelativePath -replace '^\.\\', ''  # Remove leading .\
                
                Write-Host "  Adding: $RelativePath" -ForegroundColor Gray
                Write-Host "    File size: $($File.Length) bytes" -ForegroundColor DarkGray
                
                $Content += "## File: ``$RelativePath``"
                $Content += ""
                
                # Try to read file content
                try {
                    $FileContent = Get-Content -Path $File.FullName -Raw -ErrorAction Stop
                    
                    # Determine file type for syntax highlighting
                    $Extension = $File.Extension.ToLower()
                    $Language = switch ($Extension) {
                        ".py" { "python" }
                        ".js" { "javascript" }
                        ".json" { "json" }
                        ".yaml" { "yaml" }
                        ".yml" { "yaml" }
                        ".md" { "markdown" }
                        ".toml" { "toml" }
                        ".txt" { "text" }
                        ".ps1" { "powershell" }
                        ".sh" { "bash" }
                        ".html" { "html" }
                        ".css" { "css" }
                        ".xml" { "xml" }
                        default { "text" }
                    }
                    
                    if ([string]::IsNullOrWhiteSpace($FileContent)) {
                        $Content += "*File is empty*"
                    } else {
                        $Content += "````$Language"
                        $Content += $FileContent
                        $Content += "````"
                    }
                } catch {
                    $Content += "*Could not read file content (binary or access denied)*"
                    Write-Warning "Could not read: $RelativePath - $($_.Exception.Message)"
                }
                
                $Content += ""
                $Content += "---"
                $Content += ""
                $FileCount++
                
            } catch {
                Write-Warning "Error processing file $($File.FullName): $($_.Exception.Message)"
            }
        }
    } else {
        Write-Warning "Directory not found: $Dir"
    }
}

# Write consolidated content to output file
try {
    $Content | Out-File -FilePath $OutputFile -Encoding UTF8
    Write-Host ""
    Write-Host "Consolidation complete!" -ForegroundColor Green
    Write-Host "Files processed: $FileCount" -ForegroundColor Cyan
    Write-Host "Output written to: $OutputFile" -ForegroundColor Cyan
    Write-Host "File size: $((Get-Item $OutputFile).Length / 1KB) KB" -ForegroundColor Cyan
} catch {
    Write-Error "Failed to write output file: $($_.Exception.Message)"
    exit 1
}

Write-Host ""
Write-Host "You can now upload '$OutputFile' for review." -ForegroundColor Green
