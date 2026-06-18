param(
    [switch]$n,  # Non-interactive mode: assume yes to upgrades
    [switch]$y   # Yes to upgrades
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$venvName = ".venv"

Write-Host -ForegroundColor DarkMagenta "--- Environment Setup ---"

# --- Project Root ---
# The project root is the exact directory where this script file is located.
if ([string]::IsNullOrWhiteSpace($PSScriptRoot)) {
    Write-Host -ForegroundColor Red "ERROR: Unable to determine script location using `$PSScriptRoot."
    Write-Host -ForegroundColor Cyan "Please run this as a .ps1 script file, not as pasted commands."
    exit 1
}

$projectRoot = $PSScriptRoot

if (-not (Test-Path (Join-Path $projectRoot "pyproject.toml"))) {
    Write-Host -ForegroundColor Red "ERROR: Cannot find pyproject.toml in script directory:"
    Write-Host -ForegroundColor Red "  $projectRoot"
    Write-Host -ForegroundColor Cyan "The script must be located directly inside the project root."
    exit 1
}

# Change to project root directory.
Set-Location -LiteralPath $projectRoot

$venvPath = Join-Path -Path $projectRoot -ChildPath $venvName

# --- Logging ---
# Logs are stored in: project-root\logs\bootstrap.log
$logsDir = Join-Path -Path $projectRoot -ChildPath "logs"
$logPath = Join-Path -Path $logsDir -ChildPath "bootstrap.log"

if (-not (Test-Path $logsDir)) {
    New-Item -Path $logsDir -ItemType Directory -Force | Out-Null
}

"$(Get-Date): Bootstrap started in $projectRoot" | Out-File $logPath -Encoding utf8 -Force

$transcriptStarted = $false

try {
    Start-Transcript -Path $logPath -Append
    $transcriptStarted = $true

    Write-Host -ForegroundColor Gray "Logging to: $logPath"
    Write-Host -ForegroundColor Green "Project root: $projectRoot"
    Write-Host -ForegroundColor Green "Working directory set to project root."

    # --- Pre-flight Checks ---

    function Test-PythonCommand {
        param(
            [Parameter(Mandatory = $true)]
            [string]$Command,

            [string[]]$Arguments = @(),

            [Parameter(Mandatory = $true)]
            [string]$Source
        )

        try {
            $probe = @'
import sys
print(sys.executable)
print(".".join(map(str, sys.version_info[:3])))
'@

            $output = @(& $Command @Arguments -c $probe 2>$null)

            if (-not $output -or $output.Count -lt 2) {
                return $null
            }

            $exe = [string]$output[0]
            $versionText = [string]$output[1]

            $exe = $exe.Trim()
            $versionText = $versionText.Trim()

            if ([string]::IsNullOrWhiteSpace($exe) -or [string]::IsNullOrWhiteSpace($versionText)) {
                return $null
            }

            $versionParts = $versionText -split '\.' | ForEach-Object { [int]$_ }

            if ($versionParts.Count -lt 2) {
                return $null
            }

            return [pscustomobject]@{
                Executable   = $exe
                VersionText  = $versionText
                VersionParts = $versionParts
                Source       = $Source
            }
        }
        catch {
            return $null
        }
    }

    function Resolve-PythonExe {
        $candidates = @()

        if (-not [string]::IsNullOrWhiteSpace($env:PYTHON)) {
            $candidates += [pscustomobject]@{
                Command   = $env:PYTHON
                Arguments = @()
                Source    = "PYTHON environment variable"
            }
        }

        $candidates += [pscustomobject]@{
            Command   = "py"
            Arguments = @("-3.12")
            Source    = "Windows Python launcher: py -3.12"
        }

        $candidates += [pscustomobject]@{
            Command   = "py"
            Arguments = @("-3")
            Source    = "Windows Python launcher: py -3"
        }

        $candidates += [pscustomobject]@{
            Command   = "python"
            Arguments = @()
            Source    = "PATH command: python"
        }

        $candidates += [pscustomobject]@{
            Command   = "python3"
            Arguments = @()
            Source    = "PATH command: python3"
        }

        $tested = @()

        foreach ($candidate in $candidates) {
            $result = Test-PythonCommand -Command $candidate.Command -Arguments $candidate.Arguments -Source $candidate.Source

            if ($null -eq $result) {
                $tested += "$($candidate.Source): not found or not usable"
                continue
            }

            $tested += "$($result.Source): Python $($result.VersionText) at $($result.Executable)"

            $major = $result.VersionParts[0]
            $minor = $result.VersionParts[1]

            if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 12)) {
                return $result
            }
        }

        Write-Host -ForegroundColor Red "ERROR: Python 3.12 or newer is required."
        Write-Host -ForegroundColor Yellow "Checked Python candidates:"

        foreach ($item in $tested) {
            Write-Host -ForegroundColor Yellow "  $item"
        }

        exit 1
    }

    $pythonInfo = Resolve-PythonExe
    $pythonExe = $pythonInfo.Executable
    $pyVersion = $pythonInfo.VersionText

    Write-Host -ForegroundColor Cyan "Using Python executable: $pythonExe"
    Write-Host -ForegroundColor Cyan "Python source: $($pythonInfo.Source)"
    Write-Host -ForegroundColor Cyan "Python version: $pyVersion"

    # --- Ensure Virtual Environment Exists ---
    if (-not (Test-Path $venvPath)) {
        Write-Host -ForegroundColor Yellow "No virtual environment found. Creating new one at '$venvPath'..."
        & $pythonExe -m venv $venvPath
    }
    else {
        Write-Host -ForegroundColor Green "Existing virtual environment found at '$venvPath'."
    }

    # Path to venv python.
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

    $currentPip = try {
        & "$venvPython" -m pip show pip 2>$null | Select-String "Version: (.*)" | ForEach-Object { $_.Matches.Groups[1].Value }
    }
    catch {
        "Not Installed"
    }

    if (-not $currentPip) {
        $currentPip = "Not Installed"
    }

    $currentSetuptools = try {
        & "$venvPython" -m pip show setuptools 2>$null | Select-String "Version: (.*)" | ForEach-Object { $_.Matches.Groups[1].Value }
    }
    catch {
        "Not Installed"
    }

    if (-not $currentSetuptools) {
        $currentSetuptools = "Not Installed"
    }

    $currentWheel = try {
        & "$venvPython" -m pip show wheel 2>$null | Select-String "Version: (.*)" | ForEach-Object { $_.Matches.Groups[1].Value }
    }
    catch {
        "Not Installed"
    }

    if (-not $currentWheel) {
        $currentWheel = "Not Installed"
    }

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
        Write-Host -ForegroundColor Gray "Non-interactive mode: Upgrading pip/setuptools/wheel..."
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
            Write-Host -ForegroundColor Gray "Skipping upgrades."
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

    # --- Install the package in editable mode ---
    Write-Host -ForegroundColor Cyan "Installing package (editable) with core and dev dependencies from pyproject.toml..."
    & "$venvPython" -m pip install -e ".[dev]" 2>&1

    if ($LASTEXITCODE -ne 0) {
        Write-Host -ForegroundColor Red "Installation failed. Check $logPath for details."
        Write-Host -ForegroundColor Yellow "This can happen when pip/setuptools/wheel are outdated. Please update and try again."

        if (-not $n) {
            Write-Host -ForegroundColor Yellow "Press any key to continue..."
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        }

        exit 1
    }

    Write-Host -ForegroundColor Green "Installation complete!"
    Write-Host -ForegroundColor Green "--- SETUP SUCCESSFUL ---"
    Write-Host -ForegroundColor White "------------------------"
    Write-Host -ForegroundColor Cyan "To activate the virtual environment, run:  .\.venv\Scripts\Activate.ps1"
    Write-Host -ForegroundColor Cyan "To exit the virtual environment, run:  deactivate"
}
catch {
    Write-Host -ForegroundColor Red "ERROR: Setup failed: $_"
    exit 1
}
finally {
    if ($transcriptStarted) {
        Stop-Transcript
    }
}