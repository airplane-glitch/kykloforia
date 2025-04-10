import os
import shutil
import time
from pathlib import Path
from datetime import datetime
from tkinter import Tk, filedialog

# Select directories with UI
root = Tk()
root.withdraw()  # Hide the main Tkinter window

print("Select the folder where logs are being written:")
LOG_DIR = Path(filedialog.askdirectory(title="Select Log Directory"))

print("Select the folder where logs should be backed up:")
ARCHIVE_DIR = Path(filedialog.askdirectory(title="Select Archive Directory"))

CHECK_INTERVAL = 60  # How often to check for new logs (in seconds)

# Ensure archive directory exists
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


def get_log_files():
    """Returns a list of log files sorted by modification time."""
    log_files = sorted(LOG_DIR.glob("messages.log*"), key=lambda f: f.stat().st_mtime)
    print(f"[DEBUG] Found log files: {[f.name for f in log_files]}")  # Debug print
    return log_files


def move_old_logs():
    """Moves log files to the archive directory before they are overwritten."""
    log_files = get_log_files()

    for log_file in log_files:
        if not log_file.is_file():  # Ensure it's a valid file
            continue

        # Generate a timestamped filename for the archived log
        timestamp = datetime.now().strftime("%m-%d-%y-%H-%M-%S")
        archive_filename = f"copied_{timestamp}.log"
        archive_path = ARCHIVE_DIR / archive_filename

        # Only move if the file isn't being actively written (simple check: hasn't changed in last CHECK_INTERVAL seconds)
        initial_size = log_file.stat().st_size
        print(f"[DEBUG] Checking file: {log_file.name}, Initial size: {initial_size} bytes")
        time.sleep(CHECK_INTERVAL)
        new_size = log_file.stat().st_size
        print(f"[DEBUG] After {CHECK_INTERVAL}s, new size: {new_size} bytes")

        if initial_size == new_size:
            if not archive_path.exists():
                print(f"Moving {log_file} to archive as {archive_filename}.")
                shutil.move(str(log_file), str(archive_path))
            else:
                print(f"[DEBUG] Archive file already exists: {archive_filename}, skipping move.")
        else:
            print(f"[DEBUG] File {log_file.name} is still growing, skipping move.")


if __name__ == "__main__":
    print("Starting log monitor...")
    while True:
        move_old_logs()
        time.sleep(CHECK_INTERVAL)
