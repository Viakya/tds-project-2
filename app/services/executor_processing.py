import subprocess
import tempfile
import os
import uuid
import shutil

# Only block actually dangerous things
FORBIDDEN_KEYWORDS = [
    "subprocess",
    "os.remove(",
    "os.rmdir(",
    "rm -rf",
    "sudo ",
    "apt-get",
    "pip install",
]


def script_safe(script: str) -> bool:
    """Return False if script contains dangerous operations."""
    for bad in FORBIDDEN_KEYWORDS:
        if bad in script:
            return False
    return True


def run_processing_script(script: str, scraped_folder: str):
    """
    Executes a data processing script in an isolated temp dir.

    Steps:
      1. Create temp workspace
      2. Copy all scraped files & folders into workspace
      3. Write processor.py
      4. Execute processor.py
      5. Return stdout, stderr, output_folder
    """

    # ----- SAFETY CHECK -----
    if not script_safe(script):
        return {"error": "Unsafe processing script. Aborted."}

    # ----- CREATE TEMP FOLDER -----
    run_id = str(uuid.uuid4())
    temp_dir = os.path.join(tempfile.gettempdir(), f"processor_{run_id}")
    os.makedirs(temp_dir, exist_ok=True)

    # ----- COPY SCRAPED FILES INTO PROCESSING WORKSPACE -----
    for f in os.listdir(scraped_folder):
        src = os.path.join(scraped_folder, f)
        dst = os.path.join(temp_dir, f)

        # If it's a directory -> copy tree
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)

    # ----- WRITE PROCESSOR SCRIPT -----
    script_path = os.path.join(temp_dir, "processor.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script)

    # ----- EXECUTE SCRIPT -----
    try:
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=temp_dir
        )
    except subprocess.TimeoutExpired:
        return {"error": "Processing script timeout."}

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "output_folder": temp_dir
    }
