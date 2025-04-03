# Detect the OS
$OS = $env:OS

# Check if venv exists, if not, create it
if (!(Test-Path "venv")) {
    python -m venv venv
}

# Windows Setup
if ($OS -match "Windows") {
    # Activate virtual environment
    .\venv\Scripts\Activate

    # Upgrade pip
    python.exe -m pip install --upgrade pip

    # Install dependencies
    pip install -r requirements.txt
}

# Linux/macOS Setup
else {
    # Use Bash to execute Linux commands
    bash -c "
    source venv/bin/activate &&
    python3 -m pip install --upgrade pip &&
    pip install -r requirements.txt
    "
}

Write-Output "✅ Virtual environment setup complete!"
