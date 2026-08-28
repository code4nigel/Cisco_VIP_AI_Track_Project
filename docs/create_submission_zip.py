import os
import zipfile

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_ZIP = os.path.join(PROJECT_ROOT, "NetSage_AI_Cisco_VIP_Project_Submission.zip")

EXCLUDE_DIRS = {".venv", ".git", "__pycache__", ".pytest_cache", "seabed", ".idea", ".vscode"}
EXCLUDE_FILES = {".env", ".DS_Store", "NetSage_AI_Cisco_VIP_Project_Submission.zip"}
EXCLUDE_EXTS = {".pyc", ".pyo"}

print(f"Packaging submission zip from: {PROJECT_ROOT}")
print(f"Destination: {OUTPUT_ZIP}")

included_files_count = 0
with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Filter directories in-place
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".venv")]
        
        for file in files:
            # Exclude temp lock files, sensitive files, and binary bytecode
            if file.startswith("~$") or file in EXCLUDE_FILES or file.endswith(tuple(EXCLUDE_EXTS)):
                continue
            
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, PROJECT_ROOT)
            
            zipf.write(abs_path, rel_path)
            included_files_count += 1
            print(f"  + Added: {rel_path}")

print(f"\n[SUCCESS] Successfully packaged {included_files_count} clean files into: {OUTPUT_ZIP}")
size_kb = os.path.getsize(OUTPUT_ZIP) / 1024
print(f"Archive Size: {size_kb:.1f} KB ({size_kb/1024:.2f} MB)")
