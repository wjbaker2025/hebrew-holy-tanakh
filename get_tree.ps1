function Show-Tree {
    param(
        [string]$Path = ".",
        [string]$Indent = "",
        [string[]]$Exclude = @("__pycache__", ".mypy_cache", ".git", ".venv", ".pytest_cache", "node_modules", "*.pyc", "Legacy", "WPy64-31241", "VSCode-win32-x64-1.107.0", "LMStudio", ".OLD", ".ruff_cache", ".vscode", "dist", "build", "*.log", ".DS_Store", "Thumbs.db", ".pytest_cache", ".mypy_cache", ".tox", ".coverage", "htmlcov", ".cache", ".eggs", "*.egg-info")
    )
    $Items = Get-ChildItem -Path $Path | Where-Object { 
        $name = $_.Name
        ($Exclude -notcontains $name) -and !($name -like "*.pyc") -and !($name -like "*.log") -and !($name -like ".DS_Store") -and !($name -like "Thumbs.db")
    }
    $Count = $Items.Count
    if ($Count -eq 0) { return }
    for ($i = 0; $i -lt $Count; $i++) {
        $Item = $Items[$i]
        $IsLast = ($i -eq ($Count - 1))
        
        $Marker = if ($IsLast) { "└───" } else { "├───" }
        
        Write-Output "$Indent$Marker$($Item.Name)"
        
        if ($Item.PSIsContainer) {
            $NextIndent = if ($IsLast) { "$Indent    " } else { "$Indent│   " }
            Show-Tree -Path $Item.FullName -Indent $NextIndent -Exclude $Exclude
        }
    }
}
Write-Host -ForegroundColor Cyan "Generating Clean Tree..."
Show-Tree -Path "." | Out-File "tree.md" -Encoding utf8
Write-Host -ForegroundColor Green "Done! Saved to tree.md in the current directory"