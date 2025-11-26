import subprocess
import tempfile
import os
import uuid
import shutil
import json

SAFE_IMPORTS = [
    "requests",
    "pandas",
    "numpy",
    "bs4",
    "lxml",
    "json",
    "time",
    "re",
    "playwright",
    "asyncio",
]

FORBIDDEN_KEYWORDS = [
    "subprocess",
    "os.remove(",
    "os.rmdir(",
    "rm -rf",
    "sudo ",
    "apt-get",
    "pip install",
]

def is_script_safe(script: str) -> bool:
    """
    Reject scripts that contain dangerous commands.
    """
    for bad in FORBIDDEN_KEYWORDS:
        if bad in script:
            return False
    return True


def run_data_collection_script(script: str):
    """
    Runs the OpenAI-provided data collection script in a safe environment.
    
    Returns:
      {
        "stdout": "...",
        "stderr": "...",
        "data_folder": "path/to/data"
      }
    """
    if not is_script_safe(script):
        return {"error": "Unsafe script detected. Aborting."}

    # Create temp directory for script + output
    run_id = str(uuid.uuid4())
    temp_dir = os.path.join(tempfile.gettempdir(), f"collector_{run_id}")
    os.makedirs(temp_dir, exist_ok=True)

    script_path = os.path.join(temp_dir, "collector.py")

    # Write script to file
    with open(script_path, "w") as f:
        f.write(script)

    # Execute the script
    try:
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            timeout=60,  # prevent infinite loops
            cwd=temp_dir  # script writes output files here
        )
    except subprocess.TimeoutExpired:
        return {"error": "Script timed out."}

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "data_folder": temp_dir
    }
