import shutil
from pathlib import Path

original = Path("original.txt")
backup = Path("original_backup.txt")
copy_dest = Path("copy_dir/original.txt")

# Create original file
original.write_text("This is the original file content.\nLine 2.\nLine 3.\n")
print(f"Created: {original}")

# Copy file using shutil.copy
shutil.copy(original, backup)
print(f"Copied to backup: {backup}")
print("Backup content:", backup.read_text())

# Copy to another directory
copy_dest.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(original, copy_dest)  # copy2 preserves metadata
print(f"Copied with metadata to: {copy_dest}")

# Move / rename a file
moved = Path("moved.txt")
shutil.move(str(backup), str(moved))
print(f"Moved backup to: {moved}")

# Delete a file safely
original.unlink(missing_ok=True)
moved.unlink(missing_ok=True)
print("Deleted original and moved files.")

# Delete a directory tree
shutil.rmtree(copy_dest.parent, ignore_errors=True)
print(f"Removed directory: {copy_dest.parent}")
