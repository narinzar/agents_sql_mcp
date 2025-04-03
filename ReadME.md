# Python Project Template

This is a basic template for Python projects, set up with a virtual environment and dependency management. It works across **Windows**, **Linux**, and **macOS** systems. Use the provided scripts to set up the virtual environment, install dependencies, and manage your project.

## Setup Instructions

### 1. Clone the Repository
First, clone this repository to your local machine:
```bash
git clone <repo-url>
cd <repo-name>
```

### 2. Running the Setup

The repository includes a cross-platform script (`setup.ps1` for PowerShell) that automates the process of setting up your virtual environment, upgrading `pip`, and installing dependencies.

#### For Windows (PowerShell)
- Run the following command in PowerShell:
  ```powershell
  .\venv_setup_and_activate.ps1
  ```

#### For Linux/macOS (Bash)
- Run the following command in your terminal:
  ```bash
  ./venv_setup_and_activate.sh
  ```

The script will automatically check your OS and run the appropriate commands for setting up the environment.

---

## Virtual Environment

If you want to **manually create** or **recreate** the virtual environment, you can do so with the following steps:

### Create a New Virtual Environment
1. Run this command to create a new virtual environment:
   ```bash
   python -m venv venv
   ```

### Create Virtual Environment from Other Python Versions
If you want to use a specific version of Python that is not the default on your system (e.g., Python 3.11), follow these steps:

1. **Download and install the version of Python** you want to use (e.g., Python 3.11).
2. Use the following command to create a virtual environment from that specific Python version:
   ```bash
   C:\Users\YOURCOMPUTERUSERNAME\AppData\Local\Programs\Python\Python311\python.exe -m venv venv
   ```

### Activate the Virtual Environment
- On **Windows (PowerShell)**:
  ```powershell
  .\activate_venv.ps1
  ```

  *Note*: PowerShell automatically activates `venv` during the setup, so manual activation is optional.

- On **Linux/macOS (Bash)**:
  ```bash
  source venv/bin/activate
  ```

### Deactivate the Virtual Environment
To deactivate the virtual environment, simply run:
```bash
deactivate
```

### Remove and Recreate the Virtual Environment
If you need to **delete** and **recreate** the virtual environment, follow these steps:

1. Remove the existing `venv` directory:
   ```bash
   Remove-Item -Recurse -Force venv  # Windows (PowerShell)
   rm -rf venv                      # Linux/macOS (Bash)
   ```

2. Recreate the virtual environment:
   ```bash
   python -m venv venv
   ```

---

## Managing Dependencies

### Installing Dependencies
Once the virtual environment is activated, install the dependencies listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Freezing Dependencies
If you install new packages or update existing ones, remember to update `requirements.txt`:
```bash
pip freeze > requirements.txt
```

---

## Git Setup (if not already configured)
To configure Git for your project:

1. Install [Git](https://git-scm.com/downloads) if you haven't already.

2. Set your global Git configuration:
   ```bash
   git config --global user.name "Your GitHub Username"
   git config --global user.email "Your GitHub Email"
   ```

3. Restart the terminal to apply the changes.

---

## PowerShell Execution Policy (Windows)
If you're using PowerShell on Windows, you may need to change the execution policy to allow scripts to run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

This allows local scripts to run but ensures that downloaded scripts are signed.

---

## Conclusion

This template provides a ready-to-go environment for your Python project, ensuring you don't need to repeat the setup process every time. Simply use the provided scripts and enjoy a streamlined development experience!

Feel free to modify the structure or add additional tools as needed for your project.
