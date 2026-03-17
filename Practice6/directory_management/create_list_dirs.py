import os
from pathlib import Path

base = Path("workspace")

# Create nested directories
(base / "docs" / "reports").mkdir(parents=True, exist_ok=True)
(base / "src" / "utils").mkdir(parents=True, exist_ok=True)
(base / "data" / "raw").mkdir(parents=True, exist_ok=True)
print("Created nested directories under 'workspace/'")

# Create some sample files
(base / "docs" / "reports" / "report1.pdf").write_text("report 1")
(base / "docs" / "reports" / "report2.pdf").write_text("report 2")
(base / "docs" / "notes.txt").write_text("notes")
(base / "src" / "main.py").write_text("# main")
(base / "src" / "utils" / "helper.py").write_text("# helper")
(base / "data" / "raw" / "data.csv").write_text("a,b,c")

# List contents of base directory
print("\nos.listdir('workspace'):")
for item in os.listdir(base):
    print(f"  {item}")

# List all files recursively with pathlib
print("\nAll files recursively:")
for path in sorted(base.rglob("*")):
    if path.is_file():
        print(f"  {path}")

# Find files by extension
print("\n.py files:")
for py_file in sorted(base.rglob("*.py")):
    print(f"  {py_file}")

print("\n.pdf files:")
for pdf_file in sorted(base.rglob("*.pdf")):
    print(f"  {pdf_file}")

# Show current working directory
print(f"\nos.getcwd(): {os.getcwd()}")

# Cleanup
import shutil
shutil.rmtree(base, ignore_errors=True)
print("Cleaned up workspace/")
