# Check if the virtual environment exists
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "Virtual environment exists."
    # Activate the virtual environment
    .\venv\Scripts\Activate.ps1
    # Install requirements
    pip install -r requirements.txt
    Write-Host "Requirements installed successfully."
} else {
    Write-Host "Virtual environment does not exist."
    # Create a new virtual environment
    python -m venv .\venv
    # Activate the new virtual environment
    .\venv\Scripts\Activate.ps1
    # Install requirements
    pip install -r requirements.txt
    Write-Host "Virtual environment created and requirements installed."
}
