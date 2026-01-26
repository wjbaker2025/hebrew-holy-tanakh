param(
    [switch]$n,  # Non-interactive mode: assume yes to upgrades
    [switch]$y   # Yes to upgrades
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$venvName = ".venv"
$venvPath = Join-Path -Path (Get-Location) -ChildPath $venvName

Write-Host -ForegroundColor DarkMagenta "--- Environment Setup ---"

# --- Find Project Root ---
# The script can be run from anywhere, so we need to find the project root
$currentPath = Get-Location
$projectRoot = $currentPath

# Look for pyproject.toml by walking up directories if needed
while (-not (Test-Path (Join-Path $projectRoot "pyproject.toml")) -and $projectRoot -ne $projectRoot.Parent) {
    $projectRoot = $projectRoot.Parent
}

if (-not (Test-Path (Join-Path $projectRoot "pyproject.toml"))) {
    Write-Host -ForegroundColor Red "ERROR: Cannot find pyproject.toml."
    Write-Host -ForegroundColor Cyan "Please run this script from within project root or parent directory."
    exit 1
}

# Change to project root directory and initialize logging
Set-Location $projectRoot
$logPath = Join-Path $projectRoot "bootstrap.log"
"$(Get-Date): Bootstrap started in $projectRoot" | Out-File $logPath -Encoding utf8 -Force
Start-Transcript -Path $logPath -Append
Write-Host -ForegroundColor Gray "Logging to: $logPath"
Write-Host -ForegroundColor Green "Project root found at: $projectRoot"
Write-Host -ForegroundColor Green "Changed working directory to project root."

# --- Pre-flight Checks ---

# Use portable Python executable (no PATH dependency)
$portablePythonPath = Join-Path -Path $projectRoot -ChildPath "/../../Programming/WPy64-31241/python-3.12.4.amd64/python.exe"
if (-not (Test-Path $portablePythonPath)) {
    Write-Host -ForegroundColor Red "ERROR: Portable Python not found at $portablePythonPath."
    Write-Host -ForegroundColor Cyan "Please ensure the portable Python installation is available at that location."
    exit 1
}
$pythonExe = $portablePythonPath

# Verify Python version (require 3.12+)
try {
    $pyVersion = & $pythonExe -c "import sys; print('.'.join(map(str, sys.version_info[:3])))" | ForEach-Object { $_ -split '\.' | ForEach-Object { [int]$_ } }
}
catch {
    Write-Host -ForegroundColor Red "ERROR: Unable to determine Python version using $pythonExe"
    throw
}
if ($pyVersion[0] -lt 3 -or ($pyVersion[0] -eq 3 -and $pyVersion[1] -lt 12)) {
    Write-Host -ForegroundColor Red "ERROR: Python 3.12 or newer is required. Detected version: $($pyVersion -join '.')"
    exit 1
}

Write-Host -ForegroundColor Cyan "Using Python executable: $pythonExe (version $($pyVersion -join '.'))"

try {
    # --- Ensure Virtual Environment Exists ---
    if (-not (Test-Path $venvPath)) {
        Write-Host -ForegroundColor Yellow "No virtual environment found. Creating new one at '$venvPath'..."
        & $pythonExe -m venv $venvPath
    }
    else {
        Write-Host -ForegroundColor Green "Existing virtual environment found at '$venvPath'."
    }

    # Path to venv python
    $venvPython = Join-Path $venvPath "Scripts\python.exe"

    if (-not (Test-Path $venvPython)) {
        Write-Host -ForegroundColor Red "ERROR: venv python executable not found at $venvPython"
        exit 1
    }

    # --- Upgrade pip, setuptools and wheel inside the venv ---
    Write-Host -ForegroundColor Yellow "Checking pip/setuptools/wheel versions..."

    function Get-LatestPackageVersion {
        param(
            [string]$PythonExe,
            [string]$PackageName
        )
        try {
            $output = & $PythonExe -m pip index versions $PackageName 2>$null
            if ($output) {
                $latestLine = $output | Select-String "Latest version: (.*)"
                if ($latestLine) {
                    return $latestLine.Matches.Groups[1].Value.Trim()
                }
                $availableLine = $output | Select-String "Available versions: (.*)"
                if ($availableLine) {
                    return ($availableLine.Matches.Groups[1].Value.Split(',')[0].Trim())
                }
            }
        }
        catch {
        }
        return $null
    }

    $currentPip = try { & "$venvPython" -m pip show pip 2>$null | Select-String "Version: (.*)" | ForEach-Object { $_.Matches.Groups[1].Value } } catch { "Not Installed" }
    if (-not $currentPip) { $currentPip = "Not Installed" }

    $currentSetuptools = try { & "$venvPython" -m pip show setuptools 2>$null | Select-String "Version: (.*)" | ForEach-Object { $_.Matches.Groups[1].Value } } catch { "Not Installed" }
    if (-not $currentSetuptools) { $currentSetuptools = "Not Installed" }

    $currentWheel = try { & "$venvPython" -m pip show wheel 2>$null | Select-String "Version: (.*)" | ForEach-Object { $_.Matches.Groups[1].Value } } catch { "Not Installed" }
    if (-not $currentWheel) { $currentWheel = "Not Installed" }

    $latestPip = Get-LatestPackageVersion -PythonExe $venvPython -PackageName "pip"
    $latestSetuptools = Get-LatestPackageVersion -PythonExe $venvPython -PackageName "setuptools"
    $latestWheel = Get-LatestPackageVersion -PythonExe $venvPython -PackageName "wheel"

    $latestPipDisplay = if ($latestPip) { $latestPip } else { "unknown" }
    $latestSetuptoolsDisplay = if ($latestSetuptools) { $latestSetuptools } else { "unknown" }
    $latestWheelDisplay = if ($latestWheel) { $latestWheel } else { "unknown" }

    Write-Host -ForegroundColor Cyan "  pip: $currentPip (latest: $latestPipDisplay)"
    Write-Host -ForegroundColor Cyan "  setuptools: $currentSetuptools (latest: $latestSetuptoolsDisplay)"
    Write-Host -ForegroundColor Cyan "  wheel: $currentWheel (latest: $latestWheelDisplay)"

    if ($n) {
        Write-Host -ForegroundColor Grey "Non-interactive mode: Upgrading pip/setuptools/wheel..."
        & "$venvPython" -m pip install --upgrade pip setuptools wheel
        Write-Host -ForegroundColor Green "Successfully upgraded pip/setuptools/wheel."
    }
    elseif ($y) {
        Write-Host -ForegroundColor Yellow "Upgrading pip/setuptools/wheel..."
        & "$venvPython" -m pip install --upgrade pip setuptools wheel
        Write-Host -ForegroundColor Green "Successfully upgraded pip/setuptools/wheel."
    }
    else {
        $update = Read-Host "Update to latest versions? [Y/n]"
        if ($update -eq 'n' -or $update -eq 'N') {
            Write-Host -ForegroundColor Grey "Skipping upgrades."
        }
        else {
            Write-Host -ForegroundColor Yellow "Upgrading pip/setuptools/wheel..."
            & "$venvPython" -m pip install --upgrade pip setuptools wheel
            Write-Host -ForegroundColor Green "Successfully upgraded pip/setuptools/wheel."
        }
    }

    # --- Activate Virtual Environment ---
    Write-Host -ForegroundColor Yellow "Activating virtual environment (.\.venv)..."
    . .\.venv\Scripts\Activate.ps1

    # --- Install the package in editable mode (reads dependencies from pyproject.toml) ---
    Write-Host -ForegroundColor Cyan "Installing package (editable) with core and dev dependencies from pyproject.toml..."
    & "$venvPython" -m pip install -e .[dev] 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host -ForegroundColor Red "Installation failed. Check $logPath for details."
        Write-Host -ForegroundColor Yellow "This can happen when pip/setuptools/wheel are outdated. Please update and try again."
        Write-Host -ForegroundColor Yellow "Press any key to continue..."
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }
    Write-Host -ForegroundColor Green "Installation complete!"
    Write-Host -ForegroundColor Green "--- SETUP SUCCESSFUL ---"
    Write-Host -ForegroundColor White "------------------------"
    Write-Host -ForegroundColor Cyan "To activate the virtual environment, run:  .\.venv\Scripts\Activate.ps1"
    Write-Host -ForegroundColor Cyan "To exit the virtual environment, run:  deactivate"
    Stop-Transcript
}
catch {
    Write-Host -ForegroundColor Red "ERROR: Setup failed: $_"
    Stop-Transcript
    exit 1
}
