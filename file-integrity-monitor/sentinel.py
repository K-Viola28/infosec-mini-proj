import hashlib
import json
import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

BASELINE_FILE = DATA_DIR / "baseline.json"
BASELINE_HASH_FILE = DATA_DIR / "baseline.hash"
LOG_FILE = LOG_DIR / "sentinel.log"

DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def save_baseline(file_hashes):
    with open(BASELINE_FILE, "w") as file:
        json.dump(file_hashes, file, indent=4)

def load_baseline():
    try:
        with open(BASELINE_FILE, "r") as file:
            return json.load(file)

    except FileNotFoundError:
        print("❌ No baseline found.")
        print("Create one first with:")
        print("   python sentinel.py baseline")
        return None

    except json.JSONDecodeError:
        print("❌ The baseline file is corrupted.")
        return None

def scan_directory(directory):
    file_hashes = {}

    for file_path in Path(directory).rglob("*"):
        if file_path.is_file():
            file_hashes[str(file_path)] = calculate_hash(file_path)

    return file_hashes

def calculate_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(4096):
            sha256.update(chunk)

    return sha256.hexdigest()

def calculate_baseline_hash():
    return calculate_hash(BASELINE_FILE)

def compare_hashes(baseline, current):
    results = {
        "unchanged": [],
        "modified": [],
        "deleted": [],
        "new": []
    }

    for file_path in baseline:
        if file_path not in current:
            message = f"FILE DELETED | {file_path}"
            logging.warning(message)
            results["deleted"].append(file_path)

        elif baseline[file_path] != current[file_path]:
            message = f"FILE MODIFIED | {file_path}"
            logging.warning(message)
            results["modified"].append(file_path)

        else:
            message = f"FILE UNCHANGED | {file_path}"
            logging.info(message)
            results["unchanged"].append(file_path)

    for file_path in current:
        if file_path not in baseline:
            message = f"NEW FILE | {file_path}"
            logging.warning(message)
            results["new"].append(file_path)

    return results

def create_baseline(folder):
    results = scan_directory(folder)
    save_baseline(results)

    baseline_hash = calculate_baseline_hash()

    with open(BASELINE_HASH_FILE, "w") as file:
        file.write(baseline_hash)

    print("✅ Baseline created successfully.")
    print(f"📁 Files recorded: {len(results)}")

def run_scan(folder):
    baseline = load_baseline()

    if baseline is None:
        return

    if not verify_baseline():
        return

    if not Path(folder).exists():
        print(f"Folder not found: {folder}")
        return

    current = scan_directory(folder)
    results = compare_hashes(baseline, current)

    print("\n" + "=" * 55)
    print("                  SENTINEL SCAN")
    print("=" * 55)

    print(f"\nTarget: {folder}")

    print("\nResults:")

    for file_path in results["unchanged"]:
        print(f"[UNCHANGED] {file_path}")

    for file_path in results["modified"]:
        print(f"[MODIFIED]  {file_path}")

    for file_path in results["deleted"]:
        print(f"[DELETED]   {file_path}")

    for file_path in results["new"]:
        print(f"[NEW]       {file_path}")

    unchanged = len(results["unchanged"])
    modified = len(results["modified"])
    deleted = len(results["deleted"])
    new = len(results["new"])

    events = modified + deleted + new

    print("\n" + "-" * 55)
    print("SCAN SUMMARY")
    print("-" * 55)

    print(f"Unchanged: {unchanged}")
    print(f"Modified:  {modified}")
    print(f"Deleted:   {deleted}")
    print(f"New:       {new}")
    print(f"Events:    {events}")

    if events == 0:
        print("\nStatus: No changes detected.")
    else:
        print("\nStatus: Changes detected. Review the results above.")

def verify_baseline():
    try:
        with open(BASELINE_HASH_FILE, "r") as file:
            stored_hash = file.read().strip()

        current_hash = calculate_baseline_hash()

        if stored_hash != current_hash:
            print("🚨 WARNING: BASELINE HAS BEEN TAMPERED WITH!")
            return False

        return True

    except FileNotFoundError:
        print("❌ Baseline integrity information is missing.")
        return False
    
def show_menu():
    while True:
        print("\n" + "=" * 45)
        print("              S E N T I N E L")
        print("        File Integrity Monitor")
        print("=" * 45)

        print("\n1. Create baseline")
        print("2. Scan for changes")
        print("3. Verify baseline integrity")
        print("4. Exit")

        choice = input("\nSelect an option: ")

        if choice == "1":
            create_baseline(folder)

        elif choice == "2":
            run_scan(folder)

        elif choice == "3":
            if verify_baseline():
                print("✅ Baseline integrity verified.")

        elif choice == "4":
            print("\n👋 Sentinel shutting down.")
            break

        else:
            print("\n❌ Invalid option. Please choose 1-4.")

folder = BASE_DIR / "tests" / "test_folder"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_menu()

    else:
        command = sys.argv[1]

        if command == "baseline":
            create_baseline(folder)

        elif command == "scan":
            run_scan(folder)

        elif command == "verify":
            if verify_baseline():
                print("Baseline integrity verified.")

        else:
            print(f"Unknown command: {command}")