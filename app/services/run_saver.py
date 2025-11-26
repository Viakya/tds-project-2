import os, uuid, datetime, shutil

RUNS_DIR = "runs"

def create_run_folder():
    run_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + str(uuid.uuid4())
    folder = os.path.join(RUNS_DIR, run_id)
    os.makedirs(folder, exist_ok=True)
    return folder

def save_text(folder, filename, content):
    with open(os.path.join(folder, filename), "w", encoding="utf-8") as f:
        f.write(content)

def save_scraped_data(temp_folder, dest_folder):
    dest = os.path.join(dest_folder, "scraped")
    shutil.copytree(temp_folder, dest, dirs_exist_ok=True)
