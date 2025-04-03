# activate_venv.ps1

# Detect the OS
$OS = $env:OS

# Windows Setup
if ($OS -match "Windows") {
    # Activate virtual environment
    .\venv\Scripts\Activate
}

# Linux/macOS Setup
else {
    # Use Bash to execute Linux commands
    bash -c "source venv/bin/activate"
}

Write-Output "✅ Virtual environment activated!"
